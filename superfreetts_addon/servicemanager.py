from re import sub
import sys
import os
import importlib
import typing
import requests
import pprint
import functools


from . import voice as voice_module
from . import service
from . import errors
from . import version
from . import constants
# from . import constants_events removed
from . import config_models
from . import logging_utils
from . import stats
from . import performance_cache as performance
from . import voice_cache
logger = logging_utils.get_child_logger(__name__)

# don't publish more than X events for a batch uuid
COUNT_BY_BATCH_UUID = {}

# Sentry reporting removed in Lite version

class ServiceManager():
    """
    this class will discover the services that are available and query their voices. it can also route a request
    to the correct service.
    """
    def __init__(self, services_directory, package_name, allow_test_services):
        self.services_directory = services_directory
        self.package_name = package_name
        self.services = {}
        self._service_classes = {}  # Cache of ServiceBase subclasses for lazy instantiation
        self._services_initialized = False  # Track if lightweight services have been instantiated
        self._expensive_services_loaded = False  # Track if expensive services (Piper, Kokoro, MMS) are loaded
        self._configuration_model = None  # Store configuration for applying when services instantiate
        self._services_discovered = False  # Track if discover/import/cache has been performed

        
        # Performance optimization: Initialize caching layers
        # TTL cache for voice lists (1 hour expiration)
        self._voice_list_cache = performance.TTLCache(max_size=100, ttl_seconds=3600)
        # Persistent disk cache for voice lists with compression (built-in)
        cache_dir = os.path.join(os.path.dirname(services_directory), 'cache')
        self._persistent_voice_cache = voice_cache.VoiceListCache(
            cache_dir=cache_dir,
            ttl_seconds=86400  # 1 day
        )

    def configure(self, configuration_model, disable_ssl_verification: bool = False) -> bool:
        # Store configuration for applying when services are lazy-instantiated
        self._configuration_model = configuration_model

        # Clear voice list cache when configuration changes
        self.clear_voice_list_cache()

        return_value = False
        for service_name, enabled in configuration_model.get_service_enabled_map().items():
            if not self.service_exists(service_name):
                logger.debug(f'service {service_name} not yet instantiated, will configure when needed')
                continue
            service = self.get_service(service_name)
            logger.info(f'configuring service {service_name}')
            service.enabled = enabled
            if enabled:
                return_value = True
                service_config = configuration_model.get_service_config().get(service_name, {})
                service.configure(service_config)

        return return_value

    def remove_non_existent_services(self, configuration_model):
        # remove non existent services from the service enabled map
        service_enabled_map = configuration_model.get_service_enabled_map()
        service_list = list(service_enabled_map.keys())
        for service_name in service_list:
            if not self.service_exists(service_name):
                del service_enabled_map[service_name]
        # do the same thing from the service config map
        service_config_map = configuration_model.get_service_config()
        service_list = list(service_config_map.keys())
        for service_name in service_list:
            if not self.service_exists(service_name):
                del service_config_map[service_name]
        configuration_model.set_service_enabled_map(service_enabled_map)
        configuration_model.set_service_config(service_config_map)

        return configuration_model

    # =====================================
    # Service Discovery & Initialization
    # =====================================
    # Services are discovered and cached at startup for lazy initialization.
    # Services are only instantiated when first needed (configuration dialog or audio generation)
    # to keep Anki startup time fast.

    def discover_services(self):
        """Discover all files starting with service_ and ending with .py in the services directory."""
        module_names = []
        if not os.path.exists(self.services_directory):
            logger.error(f'discover_services: directory does not exist: {self.services_directory}')
            return []
            
        for filename in os.listdir(self.services_directory):
            if filename.startswith('service_') and filename.endswith('.py'):
                module_name = filename[:-3]
                # check if it's already in the list
                if module_name not in module_names:
                    module_names.append(module_name)
        
        if not module_names:
            logger.warning(f'discover_services: no service modules found in {self.services_directory}')
        return module_names

    def init_services(self):
        """
        Discover and import all service modules and cache their classes.

        This does NOT instantiate the services; that is handled by
        `instantiate_all_services()` or `instantiate_service_lazy()`.

        It is safe to call this multiple times – work will only be done once.
        """
        if self._services_discovered:
            logger.debug('init_services: services already discovered, skipping')
            return
        
        logger.info('init_services: Starting service discovery and import...')
        try:
            self.import_services()
            self._cache_service_classes()
            self._services_discovered = True
            logger.info(f'init_services: Completed. Discovered {len(self._service_classes)} service classes: {list(self._service_classes.keys())}')
        except Exception as e:
            logger.error(f'init_services: CRITICAL Error during service discovery/import: {e}', exc_info=True)
            # Ensure we can still potentially use partially discovered services
            self._services_discovered = True 
            raise

    def import_services(self):
        module_names = self.discover_services()
        logger.info(f'import_services: discovered {len(module_names)} service modules in {self.services_directory}')
        for module_name in module_names:
            try:
                full_module_path = f'{self.package_name}.{module_name}'
                logger.debug(f'import_services: attempting to import {full_module_path}')
                importlib.import_module(full_module_path)
                logger.debug(f'import_services: successfully imported {module_name}')
            except Exception as e:
                logger.error(f'import_services: failed to import module {module_name} with package {self.package_name}: {e}', exc_info=True)
                # Continue with other modules even if one fails

    def _cache_service_classes(self):
        """Cache ServiceBase subclasses without instantiating them. Called during init_services()."""
        subclasses = service.ServiceBase.__subclasses__()
        logger.debug(f'_cache_service_classes: Found {len(subclasses)} ServiceBase subclasses')
        
        for subclass in subclasses:
            try:
                # Filter out test and paid services at discovery time
                temp_instance = subclass()

                if temp_instance.test_service() and self.allow_test_services == False:
                    logger.debug(f'skipping test service {temp_instance.name}')
                    continue
                # Super Free TTS: Only cache free services
                if temp_instance.service_fee == constants.ServiceFee.paid:
                    logger.debug(f'skipping paid service {temp_instance.name}')
                    continue

                # Cache the class for later lazy instantiation
                logger.info(f'caching service class {temp_instance.name}')
                self._service_classes[temp_instance.name] = subclass
            except AttributeError as ae:
                logger.error(f'_cache_service_classes: AttributeError in {subclass.__name__}. Check for missing properties: {ae}')
                continue
            except Exception as e:
                logger.error(f'_cache_service_classes: Unexpected error caching service class {subclass.__name__}: {e}', exc_info=True)
                # Continue with other services even if one fails
                continue
        
        if len(self._service_classes) == 0:
            logger.warning('_cache_service_classes: No service classes were cached! This may indicate a problem.')

    def instantiate_all_services(self, instantiate_expensive: bool = False):
        """
        Instantiate all cached service classes and apply saved configuration.

        - Safe to call multiple times.
        - If services have not been discovered yet (for example because
          `init_services()` was never called at addon load), this will
          first discover/import/cache them to avoid empty service lists
          in configuration or voice selection UIs.
        
        **OPTIMIZATION**: Skip expensive services (Piper, Kokoro, MMS) at startup by default.
        They will be loaded on-demand using instantiate_service_lazy() when user
        actually selects them. Set instantiate_expensive=True when called from
        configuration dialog to load all services.
        
        Args:
            instantiate_expensive: If True, load Piper/Kokoro/MMS at startup (for config dialog).
                                 If False (default), defer expensive services.
        """
        # Ensure discovery/import/cache has been done
        if not self._services_discovered or not self._service_classes:
            logger.info('instantiate_all_services: services not yet discovered, running init_services() lazily')
            self.init_services()

        # Expensive services to defer unless explicitly requested (e.g., by config dialog)
        EXPENSIVE_SERVICES = {'PiperTTS', 'KokoroTTS', 'MmsTTS'}

        # If expensive services are requested but not yet loaded, load them now
        if instantiate_expensive and not self._expensive_services_loaded:
            logger.info('instantiate_all_services: Loading deferred expensive services (Piper, Kokoro, MMS)')
            loaded_expensive = []
            for service_name in EXPENSIVE_SERVICES:
                if service_name in self._service_classes and service_name not in self.services:
                    try:
                        subclass = self._service_classes[service_name]
                        instance = subclass()
                        logger.info(f'instantiating deferred expensive service {instance.name}')
                        self.services[instance.name] = instance
                        loaded_expensive.append(instance.name)
                    except Exception as e:
                        logger.error(f'Error instantiating expensive service {service_name}: {e}', exc_info=True)
            self._expensive_services_loaded = True
            logger.info(f'Expensive services loaded: {loaded_expensive}. Registered services now: {list(self.services.keys())}')
            
            # Apply configuration to newly instantiated services
            if self._configuration_model is not None:
                logger.info(f'Applying configuration from model to newly loaded expensive services')
                enabled_map = self._configuration_model.get_service_enabled_map()
                service_config = self._configuration_model.get_service_config()
                logger.debug(f'Enabled services map: {enabled_map}')
                logger.debug(f'Service configs: {list(service_config.keys())}')
                
                for service_name in loaded_expensive:
                    if service_name in self.services:
                        service = self.services[service_name]
                        enabled = enabled_map.get(service_name, False)
                        service.enabled = enabled
                        logger.info(f'Set {service_name}.enabled = {enabled}')
                        if enabled:
                            config_for_service = service_config.get(service_name, {})
                            service.configure(config_for_service)
                            logger.info(f'Applied configuration to {service_name}: {config_for_service}')
                    else:
                        logger.warning(f'Loaded expensive service {service_name} not found in self.services')
            
            # CRITICAL: Clear voice list cache since expensive services were just added
            self.clear_voice_list_cache()
            logger.info('Voice list cache cleared - expensive services now available in voice selection')
            
            # Return early ONLY IF lightweight services were already previously initialized.
            # If they aren't initialized yet, we must fall through to instantiate them now.
            if self._services_initialized:
                return

        if self._services_initialized:
            logger.debug('services already instantiated, skipping')
            return

        logger.info(f'instantiating services (expensive_services: {"included" if instantiate_expensive else "deferred"})')
        
        # Sort by priority to maintain consistent ordering
        priority_order = ["EdgeTTS", "PiperTTS", "KokoroTTS", "MmsTTS"]

        def get_priority(name):
            try:
                return priority_order.index(name)
            except ValueError:
                return 999

        sorted_names = sorted(self._service_classes.keys(), key=get_priority)

        for service_name in sorted_names:
            # Skip expensive services unless explicitly requested (instantiate_expensive=True)
            if not instantiate_expensive and service_name in EXPENSIVE_SERVICES:
                logger.info(f'deferring expensive service {service_name} - will load on-demand when needed')
                continue
            
            subclass = self._service_classes[service_name]
            instance = subclass()
            logger.info(f'instantiating service {instance.name}')
            self.services[instance.name] = instance

        deferred_count = sum(1 for s in sorted_names if (not instantiate_expensive and s in EXPENSIVE_SERVICES))
        self._services_initialized = True
        
        # Mark expensive services as loaded if we actually instantiated them
        if instantiate_expensive:
            self._expensive_services_loaded = True
            logger.info('Expensive services (Piper, Kokoro, MMS) are now loaded')
        
        logger.info(f'Services instantiated: {list(self.services.keys())} (deferred: {deferred_count})')

        # Apply saved configuration to newly instantiated services
        if self._configuration_model is not None:
            logger.info('applying saved configuration to newly instantiated services')
            self._apply_configuration_to_services(self._configuration_model)
        else:
            logger.warning('instantiate_all_services: _configuration_model is None, services will use default settings')

    def instantiate_service_lazy(self, service_name: str):
        """
        Instantiate a single service on-demand if not already instantiated.

        This is used by audio-generation paths so that we only pay the
        instantiation cost for services that are actually used.
        """
        if service_name in self.services:
            # Already instantiated
            return

        # Ensure discovery/import/cache has been done so _service_classes is populated
        if not self._services_discovered or not self._service_classes:
            logger.info('instantiate_service_lazy: services not yet discovered, running init_services() lazily')
            self.init_services()

        if service_name not in self._service_classes:
            logger.warning(f'service {service_name} not found in cached classes')
            return

        logger.info(f'lazy-instantiating service {service_name}')
        subclass = self._service_classes[service_name]
        instance = subclass()
        self.services[instance.name] = instance

        # Apply saved configuration to this newly instantiated service
        if self._configuration_model is not None:
            enabled = self._configuration_model.get_service_enabled_map().get(service_name, False)
            instance.enabled = enabled
            if enabled:
                service_config = self._configuration_model.get_service_config().get(service_name, {})
                instance.configure(service_config)

    def _apply_configuration_to_services(self, configuration_model):
        """Apply configuration to all instantiated services."""
        for service_name, enabled in configuration_model.get_service_enabled_map().items():
            if service_name not in self.services:
                logger.debug(f'service {service_name} not instantiated, skipping configuration')
                continue
            service = self.services[service_name]
            service.enabled = enabled
            if enabled:
                service_config = configuration_model.get_service_config().get(service_name, {})
                service.configure(service_config)

    def instantiate_services(self):
        """Legacy method for backwards compatibility. Calls instantiate_all_services()."""
        self.instantiate_all_services()

    # =====================================
    # Service Access
    # =====================================

    def service_exists(self, service_name):
        # Ensure services are discovered and instantiated if needed
        if not self._services_discovered or not self._service_classes:
            logger.debug('service_exists: services not yet discovered, running init_services() lazily')
            self.init_services()
        if not self._services_initialized:
            logger.debug('service_exists: services not yet instantiated, running instantiate_all_services() lazily')
            self.instantiate_all_services()
        return service_name in self.services
    
    def get_service(self, service_name):
        # **OPTIMIZATION**: Support on-demand lazy loading of expensive services
        # If service not found, try to lazy-load it (for Piper, Kokoro, MMS)
        if service_name not in self.services:
            if not self._services_initialized:
                logger.debug('get_service: services not yet instantiated, running instantiate_all_services() lazily')
                self.instantiate_all_services()
        
        # If still not found after instantiate_all_services, try lazy-load (for expensive services)
        if service_name not in self.services:
            logger.info(f'get_service: {service_name} not found, attempting lazy-load')
            self.instantiate_service_lazy(service_name)
        
        return self.services.get(service_name)

    def get_all_services(self):
        """
        Return all available services.
        
        Critical for Configuration dialog to show all services (including expensive ones).
        This will trigger full instantiation of all services (including Piper, Kokoro, MMS)
        to ensure config dialog shows complete list.
        """
        # Ensure services are discovered before returning list
        if not self._services_discovered or not self._service_classes:
            logger.info('get_all_services: services not yet discovered, running init_services() lazily')
            self.init_services()
        
        # If services not yet initialized, instantiate lightweight ones first
        if not self._services_initialized:
            logger.info('get_all_services: instantiating lightweight services')
            self.instantiate_all_services(instantiate_expensive=False)
        
        # If expensive services NOT yet loaded, load them now (for config dialog)
        if not self._expensive_services_loaded:
            logger.info('get_all_services: loading expensive services (Piper, Kokoro, MMS) for config dialog')
            # Load the deferred expensive services
            EXPENSIVE_SERVICES = {'PiperTTS', 'KokoroTTS', 'MmsTTS'}
            for service_name in EXPENSIVE_SERVICES:
                if service_name not in self.services:
                    self.instantiate_service_lazy(service_name)
            self._expensive_services_loaded = True
        
        services_list = list(self.services.values())
        logger.debug(f'get_all_services: Returning {len(services_list)} services: {[s.name for s in services_list]}')
        return services_list

    # =====================================
    # Service Configuration
    # =====================================


    def service_configuration_options(self, service_name):
        # Ensure services are instantiated before accessing configuration
        if not self._services_initialized:
            logger.debug('service_configuration_options: services not yet instantiated, running instantiate_all_services() lazily')
            # Try lightweight first, then force expensive if needed
            self.instantiate_all_services(instantiate_expensive=False)
        
        # If service still not found (expensive service was deferred), lazy-load it
        if service_name not in self.services:
            logger.info(f'service_configuration_options: {service_name} not found, attempting lazy-load')
            self.instantiate_service_lazy(service_name)
        
        return self.services.get(service_name, {}).configuration_options() if service_name in self.services else {}

    # =====================================
    # Audio Generation & Voice Management
    # =====================================


    def get_tts_audio(self, source_text, voice: voice_module.TtsVoice_v3, options, audio_request_context):
        logger.debug(f'get_tts_audio for voice: {voice}')
        # assert the type of voice being passed in
        assert isinstance(voice, voice_module.TtsVoice_v3), f"Expected voice to be TtsVoice_v3, got {type(voice).__name__}"
        return self.get_tts_audio_implementation(source_text, voice, options, audio_request_context)

    def get_tts_audio_implementation(self, source_text, voice: voice_module.TtsVoice_v3, options, audio_request_context):
        logger.debug(f'get_tts_audio_implementation for voice: {voice}, source_text: {source_text}')


        # Ensure service is instantiated before accessing it
        self.instantiate_service_lazy(voice.service)
        if voice.service not in self.services:
            raise errors.ServiceException(f'Service {voice.service} could not be instantiated')
        service = self.services[voice.service]
        logger.debug(f'voice: {voice}, using service {service.name}')
        return service.get_tts_audio(source_text, voice, options)

    def get_tts_audio_batch(self, source_texts: typing.List[str], voice: voice_module.TtsVoice_v3, options: dict) -> typing.List[typing.Optional[bytes]]:
        logger.debug(f'get_tts_audio_batch for voice: {voice}, count: {len(source_texts)}')
        assert isinstance(voice, voice_module.TtsVoice_v3), f"Expected voice to be TtsVoice_v3, got {type(voice).__name__}"
        
        # Ensure service is instantiated before accessing it
        self.instantiate_service_lazy(voice.service)
        if voice.service not in self.services:
            raise errors.ServiceException(f'Service {voice.service} could not be instantiated')
        
        service = self.services[voice.service]
        return service.get_tts_audio_batch(source_texts, voice, options)

    def full_voice_list(self, single_service_name=None) -> typing.List[voice_module.TtsVoice_v3]:
        # Ensure services are discovered, instantiated, and configured before trying to get voice lists
        # This handles the case where voice selection is accessed before configuration dialog
        if not self._services_discovered or not self._service_classes:
            logger.info('full_voice_list: services not yet discovered, running init_services() lazily')
            self.init_services()
        if not self._services_initialized:
            logger.info('full_voice_list: Services not yet initialized, instantiating now to load voice lists')
            # Load expensive services too (Piper, Kokoro, MMS) since user is accessing voice selection
            self.instantiate_all_services(instantiate_expensive=True)
        elif not self._expensive_services_loaded:
            # Services initialized but expensive services not yet loaded - load them now
            logger.info('full_voice_list: Services initialized but expensive services not loaded, loading now')
            self.instantiate_all_services(instantiate_expensive=True)

        # Check persistent cache first (disk-based, survives across sessions)
        cache_key = f"voice_list_{single_service_name}" if single_service_name else "voice_list_all"
        cached_voices = self._persistent_voice_cache.get(cache_key)
        if cached_voices is not None:
            logger.debug(f'full_voice_list: Returning {len(cached_voices)} voices from persistent cache')
            return cached_voices

        # Check in-memory cache (TTL, faster than disk read)
        ttl_cached = self._voice_list_cache.get(cache_key)
        if ttl_cached is not None:
            logger.debug(f'full_voice_list: Returning {len(ttl_cached)} voices from TTL cache')
            return ttl_cached

        full_list = []
        enabled_count = 0
        for service_name, service_instance in self.services.items():
            if single_service_name != None:
                # we only want voices for a particular service
                if service_name != single_service_name:
                    continue
            logger.debug(f'getting voice list for service {service_name}, enabled: {service_instance.enabled}')
            if service_instance.enabled:
                enabled_count += 1
                try:
                    voices = self.get_service_voice_list(service_name)
                    logger.debug(f'got {len(voices)} voices from service {service_name}')
                    full_list.extend(voices)
                except Exception as e:
                    logger.error(f'full_voice_list: Error getting voices from service {service_name}: {e}', exc_info=True)
                    # Continue with other services even if one fails
        
        # Cache the result in both tiers for fast future access
        self._voice_list_cache.set(cache_key, full_list)
        self._persistent_voice_cache.set(cache_key, full_list)
        
        logger.info(f'full_voice_list: Returning {len(full_list)} voices from {enabled_count} enabled services (total services: {len(self.services)})')
        return full_list

    @functools.lru_cache(maxsize=None)
    def get_service_voice_list(self, service_name: str) -> typing.List[voice_module.TtsVoice_v3]:
        service_instance = self.services[service_name]
        voices = service_instance.voice_list()
        return voices

    def clear_voice_list_cache(self):
        """Clear cached voice lists so newly downloaded voices (e.g. Piper) appear in the UI."""
        self.get_service_voice_list.cache_clear()
        self.locate_voice.cache_clear()
        # Also clear new caching layers
        self._voice_list_cache.clear()
        self._persistent_voice_cache.clear()

    def deserialize_voice(self, voice_data) -> voice_module.TtsVoice_v3:
        # avoid loading voice list for services we don't need, this is particularly important for ElevenLabsCustom which does
        # an actual query to their API

        # convert voice_data to TtsVoiceId_v3
        voice_id: voice_module.TttsVoiceId_v3 = voice_module.deserialize_voice_id_v3(voice_data)

        voice_list = self.full_voice_list(single_service_name=voice_id.service)
        voice_subset = [voice for voice in voice_list if voice.get_voice_id() == voice_id]
        if len(voice_subset) == 0:
            raise errors.VoiceNotFound(voice_data)
        return voice_subset[0]

    @functools.lru_cache(maxsize=None)
    def locate_voice(self, voice_id: voice_module.TtsVoiceId_v3) -> voice_module.TtsVoice_v3:
        assert isinstance(voice_id, voice_module.TtsVoiceId_v3), f"Expected voice_id to be TtsVoiceId_v3, got {type(voice_id).__name__}"
        # convert from voice_id to actual voice
        voice_list = self.full_voice_list(single_service_name=voice_id.service)
        # logger.debug(pprint.pformat(voice_list))
        voice_subset = [voice for voice in voice_list if voice.get_voice_id() == voice_id]
        if len(voice_subset) == 0:
            logger.warning(f'could not locate voice for voice_id: {voice_id!r}')
            raise errors.VoiceIdNotFound(voice_id)
        return voice_subset[0]
