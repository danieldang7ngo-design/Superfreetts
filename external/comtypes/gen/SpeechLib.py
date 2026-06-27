from enum import IntFlag

import comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 as __wrapper_module__
from comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 import (
    ISpLexicon, SECLowConfidence, eLEXTYPE_RESERVED8,
    SAFT48kHz16BitStereo, SAFT16kHz8BitStereo,
    SGDSActiveWithAutoPause, SRTAutopause,
    DISPID_SASCurrentDevicePosition, DISPID_SVPause,
    DISPID_SGRAddResource, DISPID_SPIGrammarId, eLEXTYPE_PRIVATE12,
    STSF_CommonAppData, DISPID_SPAsItem, SREAudioLevel,
    DISPID_SPISaveToMemory, SpUnCompressedLexicon, eLEXTYPE_PRIVATE5,
    eLEXTYPE_PRIVATE20, DISPID_SPACommit, DISPID_SRCVoicePurgeEvent,
    DISPID_SGRAttributes, SPPS_SuppressWord, DISPID_SVAlertBoundary,
    DISPID_SRCRecognizer, SAFT22kHz16BitMono,
    DISPID_SRCERecognizerStateChange, SAFT32kHz8BitMono, helpstring,
    ISequentialStream, DISPID_SAStatus, DISPID_SOTRemove,
    SAFT12kHz16BitStereo, DISPID_SPPParent, SVP_5,
    DISPIDSPTSI_SelectionLength, SPEI_ACTIVE_CATEGORY_CHANGED,
    ISpVoice, DISPID_SPRulesItem, SREStreamEnd, SPAO_RETAIN_AUDIO,
    SAFTCCITT_uLaw_22kHzStereo, SREFalseRecognition,
    SPEI_PHRASE_START, SPEI_MIN_TTS, SRTStandard, SPRST_NUM_STATES,
    SpInprocRecognizer, SPRS_ACTIVE, DISPID_SGRSTNextState,
    DISPID_SVSInputSentencePosition, DISPID_SPIProperties,
    SpeechAudioProperties, DISPID_SGRsCommitAndSave, _RemotableHandle,
    SpPhraseInfoBuilder, SLOStatic, SPPROPERTYINFO, SGRSTTRule,
    eLEXTYPE_PRIVATE11, IEnumString, SPSHORTCUTPAIRLIST,
    DISPID_SVSVisemeId, SpeechCategoryRecognizers, SPPS_Interjection,
    DISPID_SRRTTickCount, DISPID_SBSWrite, SAFTCCITT_uLaw_11kHzMono,
    SVSFIsXML, SVEBookmark, DISPID_SRCEAudioLevel,
    SpCompressedLexicon, SFTSREngine, SRERequestUI,
    DISPID_SRGetRecognizers, SAFTCCITT_uLaw_44kHzStereo,
    eLEXTYPE_RESERVED10, DISPID_SPAStartElementInResult,
    DISPID_SPEs_NewEnum, DISPID_SPPNumberOfElements,
    DISPID_SPRuleFirstElement, ISpeechXMLRecoResult,
    SAFTGSM610_44kHzMono, SPINTERFERENCE_TOOSLOW, eLEXTYPE_PRIVATE1,
    SPPS_Unknown, SP_VISEME_5, DISPID_SFSClose, SpObjectTokenCategory,
    SREPropertyNumChange, DISPID_SPIReplacements, COMMETHOD,
    SAFTADPCM_11kHzMono, SGSExclusive, DISPID_SDKDeleteValue,
    SpMMAudioIn, SAFT8kHz16BitMono,
    DISPID_SLRemovePronunciationByPhoneIds, SVP_12, SPAS_RUN,
    SAFTCCITT_ALaw_11kHzMono, DISPID_SPRDisplayAttributes,
    SPEI_WORD_BOUNDARY, SpVoice, DISPIDSPTSI_SelectionOffset,
    DISPID_SGRs_NewEnum, SpShortcut, ISpeechVoice, DISPID_SGRAddState,
    wireHWND, DISPID_SRGCmdSetRuleState, SPAR_Unknown, SP_VISEME_19,
    SPRST_INACTIVE_WITH_PURGE, DISPID_SRRSpeakAudio,
    DISPID_SVEStreamStart, _check_version, eLEXTYPE_PRIVATE16,
    STCRemoteServer, SPVPRI_ALERT, DISPID_SRGId, DISPID_SABufferInfo,
    SSFMOpenForRead, DISPID_SPPBRestorePhraseFromMemory,
    DISPID_SVEBookmark, SDTPronunciation, DISPID_SABIMinNotification,
    SPEI_RESERVED5, SpWaveFormatEx, DISPID_SASNonBlockingIO,
    SpeechMicTraining, SP_VISEME_11, ISpRecognizer, SPCS_ENABLED,
    eLEXTYPE_PRIVATE15, SRTEmulated, ISpPhrase,
    SPINTERFERENCE_TOOLOUD, DISPID_SRGCmdLoadFromProprietaryGrammar,
    DISPID_SRRTimes, SPEI_RECOGNITION, DISPID_SVVoice,
    DISPID_SREmulateRecognition, ISpGrammarBuilder,
    SECFNoSpecialChars, DISPID_SVSInputSentenceLength, ULONG_PTR,
    ISpeechPhraseReplacement, STSF_LocalAppData,
    SPSMF_SAPI_PROPERTIES, SpeechAudioFormatGUIDWave, ISpRecoCategory,
    SPPHRASEELEMENT, SpeechEngineProperties, SVSFParseAutodetect,
    SPWF_SRENGINE, DISPID_SMSALineId, DISPID_SVGetVoices,
    DISPID_SVRate, SAFT48kHz8BitStereo, SVP_8, SPAO_NONE,
    DISPID_SRAllowVoiceFormatMatchingOnNextSet,
    SpeechCategoryAudioOut, DISPID_SLPSymbolic, SPSERIALIZEDRESULT,
    SDA_No_Trailing_Space, DISPID_SRGSetTextSelection,
    IServiceProvider, SpMMAudioOut, DISPID_SRCESoundEnd,
    SPPS_RESERVED1, ISpeechTextSelectionInformation,
    DISPID_SGRSTPropertyValue, SVF_None, SPEI_HYPOTHESIS,
    DISPID_SRCEEnginePrivate, DISPID_SVEventInterests,
    DISPID_SRSAudioStatus, SRARoot, SPSMF_UPS, DISPID_SBSSeek,
    DISPID_SDKGetBinaryValue, WSTRING, DISPID_SLPsCount,
    DISPID_SGRSTs_NewEnum, Speech_Default_Weight, SAFT22kHz8BitMono,
    DISPID_SOTRemoveStorageFileName,
    SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN, DISPID_SGRSRule,
    ISpeechGrammarRuleStateTransitions, ISpeechMMSysAudio,
    DISPID_SRCEBookmark, ISpObjectTokenCategory,
    SpeechAudioFormatGUIDText, DISPID_SGRSTRule, DISPID_SVEPhoneme,
    SPINTERFERENCE_NOSIGNAL, SPPS_RESERVED4, DISPID_SGRId,
    DISPID_SPEAudioStreamOffset, SVSFIsNotXML,
    DISPID_SRCEFalseRecognition, SVEPrivate, SVP_1, SP_VISEME_2,
    DISPID_SAFSetWaveFormatEx, Speech_Max_Pron_Length, SPSLMA,
    DISPID_SRAudioInputStream, SPLO_DYNAMIC, STCAll,
    DISPID_SVSCurrentStreamNumber, SBONone, SpeechGrammarTagDictation,
    ISpStreamFormat, DISPID_SPAsCount, SpTextSelectionInformation,
    SAFT12kHz8BitStereo, STCInprocServer, SPWF_INPUT,
    SAFT32kHz8BitStereo, SAFTText, SP_VISEME_1,
    SAFTCCITT_ALaw_22kHzStereo, SpeechCategoryPhoneConverters,
    DISPID_SPPFirstElement, SAFTGSM610_22kHzMono, DISPID_SGRClear,
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS, SPRULE,
    DISPID_SPPConfidence, SAFT48kHz8BitMono, ISpeechRecoContext,
    STCLocalServer, SPEI_MAX_TTS, DISPID_SRCPause,
    SpeechRegistryUserRoot, eLEXTYPE_PRIVATE3, SAFT8kHz8BitMono,
    SP_VISEME_17, DISPID_SGRsDynamic, STCInprocHandler,
    DISPID_SPRText, Speech_StreamPos_RealTime,
    ISpeechLexiconPronunciations, SSTTWildcard, DISPID_SRGState,
    DISPID_SVGetAudioInputs, SAFTCCITT_uLaw_22kHzMono,
    SRSActiveAlways, DISPID_SRGCmdLoadFromFile, SPRS_INACTIVE,
    SAFT44kHz8BitStereo, SLTApp, DISPID_SOTIsUISupported,
    DISPID_SVSpeak, SSTTDictation, SPSSuppressWord, DISPID_SPRsCount,
    ISpPhraseAlt, DISPID_SPCPhoneToId, SREAllEvents,
    DISPID_SDKEnumValues, DISPID_SRSClsidEngine, SPSFunction,
    DISPID_SRCEAdaptation, IStream, DISPID_SVEVoiceChange, SVP_9,
    ISpeechPhraseAlternates, ISpeechPhraseAlternate, DISPID_SAFType,
    SGSEnabled, DISPID_SRProfile, ISpeechAudio,
    SAFTCCITT_uLaw_8kHzMono, ISpeechPhraseProperties,
    ISpeechVoiceStatus, SINone, SpInProcRecoContext,
    DISPID_SDKSetStringValue, SRCS_Disabled,
    __MIDL___MIDL_itf_sapi_0000_0020_0001, DISPID_SOTCDefault,
    SVSFVoiceMask, DISPID_SRRSaveToMemory, DISPID_SRRAudio,
    SpeechRecoProfileProperties, SPAUDIOSTATUS,
    DISPID_SRRSetTextFeedback, SPEI_ADAPTATION, DISPID_SVDisplayUI,
    DISPID_SRSNumberOfActiveRules,
    __MIDL___MIDL_itf_sapi_0000_0020_0002, dispid, tagSTATSTG,
    SPBO_NONE, DISPID_SPRuleParent, SP_VISEME_15, SRTSMLTimeout,
    DISPID_SPEDisplayAttributes, SWPUnknownWordUnpronounceable,
    SAFTADPCM_22kHzStereo, SPLO_STATIC, DISPID_SGRSTPropertyName,
    DISPID_SRGRecoContext, SPAR_Low, SRTReSent, SRAORetainAudio,
    eLEXTYPE_PRIVATE4, ISpeechRecoGrammar, SECFIgnoreWidth, SGLexical,
    SPWORDLIST, SVSFParseMask, SpeechPropertyHighConfidenceThreshold,
    SREAdaptation, DISPIDSPTSI_ActiveOffset, SPEI_RECO_STATE_CHANGE,
    ISpMMSysAudio, WAVEFORMATEX, SFTInput, SPEI_PHONEME,
    DISPID_SABIEventBias, SGDisplay, SINoise, DISPID_SPCIdToPhone,
    ISpeechWaveFormatEx, SPWORDPRONUNCIATIONLIST, SECHighConfidence,
    DISPID_SPEsItem, DISPID_SCSBaseStream, SVSFIsFilename, SITooLoud,
    SDTLexicalForm, ISpRecoGrammar2, SPAS_STOP,
    DISPID_SVESentenceBoundary, ISpeechLexicon, SAFT22kHz16BitStereo,
    SPRST_INACTIVE, DISPID_SRCVoice, ISpeechPhraseInfo,
    DISPID_SLPPhoneIds, SREPhraseStart, ISpNotifySink,
    SPEI_FALSE_RECOGNITION, ISpStreamFormatConverter, _FILETIME,
    SpeechCategoryRecoProfiles, SPEI_SENTENCE_BOUNDARY,
    SPPHRASEPROPERTY, SpeechTokenKeyFiles, DISPID_SPCLangId,
    DISPID_SRIsUISupported, DISPID_SPERetainedStreamOffset, SPWORD,
    SECFEmulateResult, SVSFPersistXML, DISPID_SOTsCount,
    SRADefaultToActive, DISPID_SGRSTWeight,
    DISPID_SVAllowAudioOuputFormatChangesOnNextSet,
    DISPID_SRRTOffsetFromStart, SPEI_END_INPUT_STREAM,
    IInternetSecurityManager, SAFTADPCM_11kHzStereo,
    SAFT22kHz8BitStereo, DISPID_SPPsCount, DISPID_SVGetAudioOutputs,
    DISPID_SPEAudioSizeBytes, SAFT11kHz8BitStereo, SPSModifier,
    SRERecognition, DISPID_SOTGetAttribute, ISpRecoResult,
    DISPID_SLPsItem, SPEI_RESERVED2, SRSInactiveWithPurge,
    ISpeechResourceLoader, SpNotifyTranslator, SPSHORTCUTPAIR,
    ISpStream, tagSPPROPERTYINFO, DISPID_SVGetProfiles,
    eLEXTYPE_LETTERTOSOUND, SAFT32kHz16BitStereo,
    SpeechCategoryVoices, ISpProperties, ISpObjectWithToken,
    SRATopLevel, DISPID_SVEViseme, SVEVoiceChange,
    DISPID_SWFEBlockAlign, SVEAllEvents, eLEXTYPE_PRIVATE19,
    DISPID_SADefaultFormat, eLEXTYPE_RESERVED4, SVP_21,
    ISpeechGrammarRule, SP_VISEME_12, DISPID_SLPs_NewEnum,
    SpNullPhoneConverter, SPXRO_Alternates_SML,
    DISPID_SRCAudioInInterferenceStatus, DISPID_SPPs_NewEnum,
    DISPID_SRGCmdLoadFromResource, SGDSActive, SP_VISEME_6, SPAR_High,
    SAFT48kHz16BitMono, DISPID_SMSSetData, DISPID_SWFEChannels,
    SpeechAddRemoveWord, SPEI_SR_AUDIO_LEVEL, DISPID_SASetState,
    SPEI_START_SR_STREAM, __MIDL_IWinTypes_0009,
    SAFTCCITT_ALaw_11kHzStereo, SECFIgnoreCase,
    DISPID_SRGSetWordSequenceData, SRADynamic, DISPID_SVSpeakStream,
    ISpeechMemoryStream, SDA_Two_Trailing_Spaces, DISPID_SPIElements,
    SGRSTTTextBuffer, SPTEXTSELECTIONINFO,
    DISPID_SVSLastStreamNumberQueued, SPINTERFERENCE_NONE,
    SAFTADPCM_8kHzMono, DISPID_SVVolume, SPCS_DISABLED,
    DISPID_SLGetWords, DISPID_SRCEHypothesis,
    DISPID_SRCRequestedUIType, ISpeechAudioFormat, eLEXTYPE_PRIVATE6,
    SLODynamic, SP_VISEME_3, GUID, SAFTCCITT_uLaw_8kHzStereo,
    SP_VISEME_0, SPVPRI_OVER, DISPID_SABIBufferSize,
    DISPID_SRRGetXMLErrorInfo, DISPID_SASState,
    SpeechGrammarTagWildcard, DISPID_SRCERecognitionForOtherContext,
    SAFTCCITT_ALaw_8kHzStereo, SGDSInactive, DISPID_SOTsItem,
    SPSHT_OTHER, DISPID_SPARecoResult, SPSVerb, SVEWordBoundary,
    DISPMETHOD, SREBookmark, DISPID_SPEEngineConfidence,
    DISPID_SWFEAvgBytesPerSec, DISPID_SRSetPropertyString,
    SPVOICESTATUS, SRCS_Enabled, SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE,
    SPEI_END_SR_STREAM, SVESentenceBoundary, DISPID_SRCRetainedAudio,
    DISPID_SRGetPropertyNumber, DISPID_SPIEnginePrivateData,
    SGLexicalNoSpecialChars, DISPID_SRGetFormat,
    SAFTCCITT_uLaw_44kHzMono, SPEI_RESERVED1, SASStop, VARIANT_BOOL,
    DISPID_SPRuleName, DISPID_SPEsCount, SpeechCategoryAppLexicons,
    SP_VISEME_21, SVEPhoneme, SpeechTokenKeyUI, SPPS_RESERVED3,
    DISPID_SPPId, _ISpeechVoiceEvents, SpeechUserTraining,
    DISPID_SOTGetDescription, SPGS_DISABLED, SpPhoneConverter,
    DISPID_SGRSTText, SDTAlternates, _lcid, DISPID_SRGDictationUnload,
    SPDKL_LocalMachine, SAFT11kHz16BitMono, DISPID_SRCEEndStream,
    DISPID_SPIAudioSizeBytes, DISPID_SOTs_NewEnum, DISPID_SPIEngineId,
    SAFTADPCM_44kHzStereo, CoClass, SP_VISEME_9,
    SDA_Consume_Leading_Spaces, DISPID_SVSLastBookmarkId,
    SAFT16kHz16BitStereo, DISPID_SPRuleConfidence,
    SPWP_UNKNOWN_WORD_PRONOUNCEABLE, DISPID_SOTSetId, SREPrivate,
    DISPID_SDKDeleteKey, ISpeechGrammarRuleState,
    SPINTERFERENCE_NOISE, SITooSlow, DISPID_SVWaitUntilDone,
    DISPID_SRCEPhraseStart, DISPID_SPERetainedSizeBytes,
    SDKLDefaultLocation, ISpeechLexiconWord, SPSERIALIZEDPHRASE,
    SVEEndInputStream, SVSFNLPSpeakPunc, SPEI_MIN_SR,
    DISPID_SPIGetText, DISPID_SPRulesCount,
    SPSMF_SRGS_SEMANTICINTERPRETATION_W3C, ISpEventSink,
    SRSEIsSpeaking, SAFTCCITT_ALaw_44kHzStereo, SVP_18, SPPS_LMA,
    SPEI_PROPERTY_STRING_CHANGE, SREInterference, eLEXTYPE_RESERVED7,
    SPBO_AHEAD, ISpeechPhraseElements, DISPID_SRCBookmark,
    ISpeechPhoneConverter, DISPID_SOTCEnumerateTokens, STSF_AppData,
    DISPID_SLWPronunciations, DISPID_SRCState, DISPID_SLPLangId,
    DISPID_SWFEExtraData, SPDKL_DefaultLocation,
    DISPID_SPIAudioSizeTime, SPSNoun, SpeechTokenKeyAttributes,
    SSSPTRelativeToEnd, SDTAll, DISPID_SRGCommit,
    DISPID_SRGCmdLoadFromObject, SP_VISEME_16,
    ISpeechObjectTokenCategory, DISPID_SLWs_NewEnum, DISPID_SPPsItem,
    DISPID_SLWsCount, DISPID_SRRTLength, SAFT44kHz16BitStereo,
    DISPID_SRSCurrentStreamPosition, DISPID_SGRSTransitions,
    DISPID_SOTDisplayUI, SPEI_SR_PRIVATE, DISPID_SPEAudioTimeOffset,
    SAFTCCITT_ALaw_8kHzMono, SPEI_TTS_AUDIO_LEVEL, SAFT16kHz16BitMono,
    SPEI_RESERVED3, _ULARGE_INTEGER, DISPID_SVAudioOutput,
    ISpNotifySource, ISpeechObjectTokens,
    DISPID_SPIAudioStreamPosition, typelib_path, eLEXTYPE_PRIVATE2,
    Speech_Max_Word_Length, DISPID_SDKOpenKey, SPCT_SLEEP,
    DISPID_SVSLastResult, DISPID_SAVolume, SpeechCategoryAudioIn,
    SAFT8kHz8BitStereo, SP_VISEME_8, SDTReplacement,
    DISPID_SRCCmdMaxAlternates, DISPID_SASCurrentSeekPosition,
    SP_VISEME_10, DISPID_SPILanguageId, LONG_PTR, ISpeechCustomStream,
    DISPID_SPIStartTime, SVP_13, SpeechRegistryLocalMachineRoot,
    _LARGE_INTEGER, DISPID_SRGRules, SRAInterpreter,
    DISPID_SVSPhonemeId, SAFT11kHz8BitMono, ISpeechAudioBufferInfo,
    SPEI_TTS_PRIVATE, SPEI_PROPERTY_NUM_CHANGE, SPPS_Verb,
    DISPID_SPEActualConfidence, SGRSTTWildcard, SLTUser,
    SVSFParseSsml, SpeechAllElements, DISPID_SFSOpen, SRSInactive,
    ISpeechRecoResult, SVSFDefault, SVSFlagsAsync, SPGS_ENABLED,
    SVP_2, SPINTERFERENCE_TOOFAST, SSFMCreateForWrite,
    ISpeechLexiconWords, STSF_FlagCreate, DISPID_SGRsFindRule,
    SDTRule, SSTTTextBuffer, ISpeechRecoResultTimes, SPFM_NUM_MODES,
    ISpRecoContext2, SRAImport, SPEI_SR_BOOKMARK,
    DISPID_SVSInputWordLength, SPAUDIOBUFFERINFO,
    DISPID_SPELexicalForm, SPPS_Noncontent,
    SpeechPropertyResourceUsage, ISpeechPhraseProperty, SPWT_LEXICAL,
    SVP_7, DISPID_SOTCSetId, DISPID_SRCResume,
    ISpeechGrammarRuleStateTransition, SPBINARYGRAMMAR, SAFTDefault,
    SpStream, SECFDefault, DISPID_SGRsCommit, DISPID_SRCERecognition,
    DISPID_SPRuleEngineConfidence, SpLexicon, SWTDeleted,
    ISpRecoGrammar, SPSHT_EMAIL, DISPID_SLPPartOfSpeech,
    DISPID_SGRsItem, DISPID_SRGetPropertyString, ISpResourceManager,
    SASPause, ISpeechObjectToken, SPCT_SUB_DICTATION, SDTAudio,
    SVPNormal, SpStreamFormatConverter, DISPID_SLWWord, ISpShortcut,
    DISPID_SPPName, SpeechDictationTopicSpelling,
    SPEI_SR_RETAINEDAUDIO, DISPID_SRGIsPronounceable,
    ISpXMLRecoResult, SREStreamStart, DISPID_SRCreateRecoContext,
    DISPID_SPRNumberOfElements, DISPID_SOTCGetDataKey, ISpRecoContext,
    SPRS_ACTIVE_WITH_AUTO_PAUSE, DISPID_SDKGetStringValue,
    SPCT_COMMAND, SWPUnknownWordPronounceable, SVP_17,
    SPRST_ACTIVE_ALWAYS, ISpObjectToken, ISpDataKey,
    DISPID_SDKGetlongValue, SPPS_Noun, DISPID_SRRAudioFormat,
    DISPID_SVSyncronousSpeakTimeout, DISPID_SDKSetLongValue,
    DISPID_SPRuleChildren, SVEAudioLevel, SPSNotOverriden,
    SPCT_DICTATION, SAFT11kHz16BitStereo, SREStateChange, SVEViseme,
    SAFTCCITT_uLaw_11kHzStereo, DISPID_SAEventHandle,
    SPSEMANTICERRORINFO, ISpeechFileStream,
    DISPID_SPRuleNumberOfElements, SAFTNoAssignedFormat,
    SpeechTokenIdUserLexicon, DISPID_SRRDiscardResultInfo,
    SVSFPurgeBeforeSpeak, DISPID_SRCSetAdaptationData,
    DISPID_SMSGetData, DISPID_SPEPronunciation, SITooFast,
    SpPhoneticAlphabetConverter, DISPID_SRGDictationLoad,
    SGRSTTEpsilon, DISPID_SABufferNotifySize, SPWORDPRONUNCIATION,
    SAFTExtendedAudioFormat, SGSDisabled, ISpRecognizer3,
    SPEVENTSOURCEINFO, SVP_6, SGRSTTWord, SPEVENT, eWORDTYPE_DELETED,
    SPEI_TTS_BOOKMARK, DISPID_SLAddPronunciationByPhoneIds,
    ISpeechAudioStatus, SPRECOCONTEXTSTATUS,
    DISPID_SPANumberOfElementsInResult, SPCT_SUB_COMMAND,
    eLEXTYPE_PRIVATE13, SPAR_Medium, SPFM_OPEN_READONLY,
    DISPID_SVSpeakCompleteEvent, DISPID_SGRName,
    DISPID_SPRules_NewEnum, DISPID_SPPValue, DISPID_SVPriority,
    ISpeechRecognizer, ISpRecognizer2, DISPID_SPEAudioSizeTime,
    DISPID_SBSFormat, DISPID_SRRAlternates, eLEXTYPE_VENDORLEXICON,
    eLEXTYPE_USER_SHORTCUT, SPPS_Function, SPEI_SOUND_END,
    ISpSerializeState, SRERecoOtherContext, SAFT24kHz8BitStereo,
    DISPID_SRCEventInterests, SREHypothesis, SVP_3, SAFT16kHz8BitMono,
    DISPID_SWFEBitsPerSample, DISPID_SMSADeviceId,
    SGDSActiveUserDelimited, DISPID_SVSRunningState, DISPID_SRState,
    DISPID_SRSCurrentStreamNumber, SPRECOGNIZERSTATUS, SpObjectToken,
    DISPID_SRCESoundStart, SVPOver, DISPID_SDKEnumKeys, SVP_14,
    SAFTNonStandardFormat, SRAONone, eLEXTYPE_PRIVATE17,
    SWPKnownWordPronounceable, DISPID_SRCEStartStream,
    DISPID_SRAudioInput, SINoSignal, SVP_15,
    SpeechGrammarTagUnlimitedDictation, DISPID_SOTMatchesAttributes,
    SASClosed, SpFileStream, SAFT44kHz8BitMono, eLEXTYPE_RESERVED6,
    ISpeechPhraseReplacements, eLEXTYPE_PRIVATE18,
    DISPID_SRRTStreamTime, SPEI_RECO_OTHER_CONTEXT, DISPID_SVStatus,
    DISPID_SRAllowAudioInputFormatChangesOnNextSet,
    SPDKL_CurrentConfig, DISPID_SPRs_NewEnum, DISPID_SRDisplayUI,
    DISPID_SVEWord, eLEXTYPE_APP,
    SpeechPropertyLowConfidenceThreshold, SSFMOpenReadWrite, SVPAlert,
    SPEI_RESERVED6, SRSActive, SpMemoryStream, eLEXTYPE_RESERVED9,
    SPEI_MAX_SR, BSTR, DISPID_SGRInitialState, SVP_19, ISpEventSource,
    SP_VISEME_18, SpMMAudioEnum, DISPID_SRCEInterference,
    SGPronounciation, eLEXTYPE_PRIVATE14, ISpeechRecoResultDispatch,
    SPRECORESULTTIMES, DISPID_SOTGetStorageFileName,
    SPINTERFERENCE_LATENCY_WARNING, SPPS_Modifier, SPAS_PAUSE,
    SPWT_DISPLAY, SPRST_ACTIVE, SECFIgnoreKanaType,
    DISPID_SVSLastBookmark, DISPID_SOTCId, SPEI_REQUEST_UI,
    DISPID_SRSSupportedLanguages, DISPID_SMSAMMHandle,
    DISPID_SLWsItem, SRESoundEnd, DISPIDSPTSI_ActiveLength,
    DISPID_SRGCmdLoadFromMemory, SPGS_EXCLUSIVE,
    DISPID_SDKSetBinaryValue, SP_VISEME_4,
    SPWP_KNOWN_WORD_PRONOUNCEABLE, SpeechPropertyAdaptationOn,
    SWTAdded, DISPID_SRIsShared, eLEXTYPE_MORPHOLOGY, SpAudioFormat,
    SVP_0, DISPID_SRRGetXMLResult,
    SPINTERFERENCE_LATENCY_TRUNCATE_END, DISPID_SGRSTPropertyId,
    DISPID_SBSRead, DISPID_SRRecognizer, SP_VISEME_13, SVP_11,
    DISPID_SVAudioOutputStream, SVP_4, DISPID_SPERequiredConfidence,
    eLEXTYPE_PRIVATE10, DISPID_SRCCreateGrammar, ISpeechGrammarRules,
    SpCustomStream, SAFTADPCM_44kHzMono, SPXRO_SML,
    DISPID_SVEEnginePrivate, ISpeechPhraseRules, DISPID_SRStatus,
    Library, SDTProperty, SPPHRASEREPLACEMENT,
    DISPID_SRCEPropertyStringChange, HRESULT, SP_VISEME_14,
    DISPID_SVEAudioLevel, SPSHT_Unknown, DISPID_SVResume,
    SAFTGSM610_11kHzMono, ISpeechPhraseRule, SDKLLocalMachine,
    DISPID_SRCERequestUI, SRESoundStart, SAFTADPCM_22kHzMono,
    DISPID_SRCCreateResultFromMemory, SPSMF_SRGS_SAPIPROPERTIES,
    IUnknown, DISPID_SLWLangId, DISPID_SRRRecoContext,
    DISPID_SVEStreamEnd, DISPID_SDKCreateKey, DISPID_SLPType,
    DISPID_SVSInputWordPosition, SVP_20, DISPID_SGRSTType,
    SPRS_ACTIVE_USER_DELIMITED, ISpPhoneConverter,
    DISPID_SGRSAddWordTransition, SAFT24kHz8BitMono, eWORDTYPE_ADDED,
    DISPID_SPEDisplayText, ISpeechPhraseElement, SVSFParseSapi,
    SPDKL_CurrentUser, SSSPTRelativeToStart, SPBO_PAUSE,
    DISPID_SGRSTsCount, SpSharedRecoContext,
    DISPID_SASFreeBufferSpace,
    SpeechPropertyNormalConfidenceThreshold,
    DISPID_SRSetPropertyNumber, SpeechAudioVolume,
    ISpPhoneticAlphabetSelection, SPSInterjection, ISpeechBaseStream,
    SASRun, SAFTADPCM_8kHzStereo, SDKLCurrentConfig,
    DISPID_SRCRetainedAudioFormat, DISPID_SVSkip, SPAS_CLOSED,
    DISPID_SOTCategory, SpResourceManager, SPFM_OPEN_READWRITE,
    SPEI_VISEME, DISPID_SLWType, SAFT12kHz8BitMono,
    DISPID_SWFEFormatTag, DISPID_SLGetPronunciations,
    SSSPTRelativeToCurrentPosition, SRTExtendableParse,
    DISPID_SOTDataKey, ISpeechRecoResult2, DISPID_SPAs_NewEnum,
    DISPID_SLGetGenerationChange, DISPID_SPPEngineConfidence,
    DISPID_SPIGetDisplayAttributes, SPBO_TIME_UNITS,
    SAFTTrueSpeech_8kHz1BitMono, tagSPTEXTSELECTIONINFO,
    DISPID_SWFESamplesPerSec, SP_VISEME_20, SpSharedRecognizer,
    SpeechVoiceCategoryTTSRate, SPPS_NotOverriden, ISpeechDataKey,
    DISPID_SPRsItem, SPVPRI_NORMAL, DISPID_SGRSAddRuleTransition,
    SVSFNLPMask, SPFM_CREATE, SPPHRASE, VARIANT,
    DISPID_SRGCmdSetRuleIdState, SVEStartInputStream,
    SpeechTokenValueCLSID, DISPID_SRRPhraseInfo, SPEI_SOUND_START,
    SVSFUnusedFlags, DISPID_SPRFirstElement, SITooQuiet,
    DISPID_SLRemovePronunciation, ISpNotifyTranslator,
    SREPropertyStringChange, DISPID_SRGReset, SPINTERFERENCE_TOOQUIET,
    SPEI_VOICE_CHANGE, SVP_16, ISpeechLexiconPronunciation,
    DISPID_SPPChildren, SPWT_PRONUNCIATION, DISPID_SOTCreateInstance,
    SPSUnknown, _ISpeechRecoContextEvents, SGRSTTDictation,
    SAFT32kHz16BitMono, DISPID_SGRSTsItem, SDTDisplayText,
    SECNormalConfidence, SAFT24kHz16BitMono, ISpeechPhraseInfoBuilder,
    SPWT_LEXICAL_NO_SPECIAL_CHARS, DISPID_SPIRule, DISPID_SGRsCount,
    DISPID_SAFGetWaveFormatEx, IEnumSpObjectTokens,
    SPFM_CREATE_ALWAYS, SVP_10, SPPS_RESERVED2,
    DISPID_SRGDictationSetState, DISPID_SGRSAddSpecialTransition,
    UINT_PTR, SAFTGSM610_8kHzMono, SPEI_UNDEFINED, ISpAudio,
    SpeechVoiceSkipTypeSentence, SAFT8kHz16BitStereo, eLEXTYPE_USER,
    DISPID_SPAPhraseInfo, SAFT44kHz16BitMono, DISPID_SLGenerationId,
    ISpeechRecognizerStatus, SpeechPropertyComplexResponseSpeed,
    Speech_StreamPos_Asap, DISPID_SRCEPropertyNumberChange,
    DISPID_SLAddPronunciation, eLEXTYPE_PRIVATE7, SBOPause,
    IInternetSecurityMgrSite, DISPID_SPRuleId, SRAExport,
    SPSHT_NotOverriden, SAFTCCITT_ALaw_44kHzMono,
    SAFTCCITT_ALaw_22kHzMono, SVF_Stressed, SAFT24kHz16BitStereo,
    SDA_One_Trailing_Space, eLEXTYPE_PRIVATE9, DISPID_SGRsAdd,
    SpeechPropertyResponseSpeed, SPPHRASERULE, DISPID_SVIsUISupported,
    DISPID_SAFGuid, SSFMCreate, DISPID_SPIRetainedSizeBytes,
    SPEI_START_INPUT_STREAM, ISpPhoneticAlphabetConverter,
    DISPID_SOTId, SAFT12kHz16BitMono, SDKLCurrentUser, SVF_Emphasis,
    eLEXTYPE_PRIVATE8, SP_VISEME_7, SRSEDone, SPEI_INTERFERENCE
)


class SpeechWordType(IntFlag):
    SWTAdded = 1
    SWTDeleted = 2


class DISPID_SpeechVoice(IntFlag):
    DISPID_SVStatus = 1
    DISPID_SVVoice = 2
    DISPID_SVAudioOutput = 3
    DISPID_SVAudioOutputStream = 4
    DISPID_SVRate = 5
    DISPID_SVVolume = 6
    DISPID_SVAllowAudioOuputFormatChangesOnNextSet = 7
    DISPID_SVEventInterests = 8
    DISPID_SVPriority = 9
    DISPID_SVAlertBoundary = 10
    DISPID_SVSyncronousSpeakTimeout = 11
    DISPID_SVSpeak = 12
    DISPID_SVSpeakStream = 13
    DISPID_SVPause = 14
    DISPID_SVResume = 15
    DISPID_SVSkip = 16
    DISPID_SVGetVoices = 17
    DISPID_SVGetAudioOutputs = 18
    DISPID_SVWaitUntilDone = 19
    DISPID_SVSpeakCompleteEvent = 20
    DISPID_SVIsUISupported = 21
    DISPID_SVDisplayUI = 22


class DISPID_SpeechPhraseRules(IntFlag):
    DISPID_SPRulesCount = 1
    DISPID_SPRulesItem = 0
    DISPID_SPRules_NewEnum = -4


class SPAUDIOOPTIONS(IntFlag):
    SPAO_NONE = 0
    SPAO_RETAIN_AUDIO = 1


class DISPID_SpeechLexicon(IntFlag):
    DISPID_SLGenerationId = 1
    DISPID_SLGetWords = 2
    DISPID_SLAddPronunciation = 3
    DISPID_SLAddPronunciationByPhoneIds = 4
    DISPID_SLRemovePronunciation = 5
    DISPID_SLRemovePronunciationByPhoneIds = 6
    DISPID_SLGetPronunciations = 7
    DISPID_SLGetGenerationChange = 8


class SpeechGrammarState(IntFlag):
    SGSEnabled = 1
    SGSDisabled = 0
    SGSExclusive = 3


class SPADAPTATIONRELEVANCE(IntFlag):
    SPAR_Unknown = 0
    SPAR_Low = 1
    SPAR_Medium = 2
    SPAR_High = 3


class SpeechRuleAttributes(IntFlag):
    SRATopLevel = 1
    SRADefaultToActive = 2
    SRAExport = 4
    SRAImport = 8
    SRAInterpreter = 16
    SRADynamic = 32
    SRARoot = 64


class DISPID_SpeechLexiconWords(IntFlag):
    DISPID_SLWsCount = 1
    DISPID_SLWsItem = 0
    DISPID_SLWs_NewEnum = -4


class SpeechLexiconType(IntFlag):
    SLTUser = 1
    SLTApp = 2


class SpeechPartOfSpeech(IntFlag):
    SPSNotOverriden = -1
    SPSUnknown = 0
    SPSNoun = 4096
    SPSVerb = 8192
    SPSModifier = 12288
    SPSFunction = 16384
    SPSInterjection = 20480
    SPSLMA = 28672
    SPSSuppressWord = 61440


class DISPID_SpeechLexiconWord(IntFlag):
    DISPID_SLWLangId = 1
    DISPID_SLWType = 2
    DISPID_SLWWord = 3
    DISPID_SLWPronunciations = 4


class SpeechDataKeyLocation(IntFlag):
    SDKLDefaultLocation = 0
    SDKLCurrentUser = 1
    SDKLLocalMachine = 2
    SDKLCurrentConfig = 5


class DISPID_SpeechLexiconProns(IntFlag):
    DISPID_SLPsCount = 1
    DISPID_SLPsItem = 0
    DISPID_SLPs_NewEnum = -4


class DISPID_SpeechVoiceStatus(IntFlag):
    DISPID_SVSCurrentStreamNumber = 1
    DISPID_SVSLastStreamNumberQueued = 2
    DISPID_SVSLastResult = 3
    DISPID_SVSRunningState = 4
    DISPID_SVSInputWordPosition = 5
    DISPID_SVSInputWordLength = 6
    DISPID_SVSInputSentencePosition = 7
    DISPID_SVSInputSentenceLength = 8
    DISPID_SVSLastBookmark = 9
    DISPID_SVSLastBookmarkId = 10
    DISPID_SVSPhonemeId = 11
    DISPID_SVSVisemeId = 12


class DISPID_SpeechLexiconPronunciation(IntFlag):
    DISPID_SLPType = 1
    DISPID_SLPLangId = 2
    DISPID_SLPPartOfSpeech = 3
    DISPID_SLPPhoneIds = 4
    DISPID_SLPSymbolic = 5


class DISPID_SpeechPhoneConverter(IntFlag):
    DISPID_SPCLangId = 1
    DISPID_SPCPhoneToId = 2
    DISPID_SPCIdToPhone = 3


class SpeechGrammarWordType(IntFlag):
    SGDisplay = 0
    SGLexical = 1
    SGPronounciation = 2
    SGLexicalNoSpecialChars = 3


class SpeechSpecialTransitionType(IntFlag):
    SSTTWildcard = 1
    SSTTDictation = 2
    SSTTTextBuffer = 3


class DISPID_SpeechVoiceEvent(IntFlag):
    DISPID_SVEStreamStart = 1
    DISPID_SVEStreamEnd = 2
    DISPID_SVEVoiceChange = 3
    DISPID_SVEBookmark = 4
    DISPID_SVEWord = 5
    DISPID_SVEPhoneme = 6
    DISPID_SVESentenceBoundary = 7
    DISPID_SVEViseme = 8
    DISPID_SVEAudioLevel = 9
    DISPID_SVEEnginePrivate = 10


class DISPID_SpeechRecognizer(IntFlag):
    DISPID_SRRecognizer = 1
    DISPID_SRAllowAudioInputFormatChangesOnNextSet = 2
    DISPID_SRAudioInput = 3
    DISPID_SRAudioInputStream = 4
    DISPID_SRIsShared = 5
    DISPID_SRState = 6
    DISPID_SRStatus = 7
    DISPID_SRProfile = 8
    DISPID_SREmulateRecognition = 9
    DISPID_SRCreateRecoContext = 10
    DISPID_SRGetFormat = 11
    DISPID_SRSetPropertyNumber = 12
    DISPID_SRGetPropertyNumber = 13
    DISPID_SRSetPropertyString = 14
    DISPID_SRGetPropertyString = 15
    DISPID_SRIsUISupported = 16
    DISPID_SRDisplayUI = 17
    DISPID_SRGetRecognizers = 18
    DISPID_SVGetAudioInputs = 19
    DISPID_SVGetProfiles = 20


class SpeechStreamSeekPositionType(IntFlag):
    SSSPTRelativeToStart = 0
    SSSPTRelativeToCurrentPosition = 1
    SSSPTRelativeToEnd = 2


class SpeechStreamFileMode(IntFlag):
    SSFMOpenForRead = 0
    SSFMOpenReadWrite = 1
    SSFMCreate = 2
    SSFMCreateForWrite = 3


class SPDATAKEYLOCATION(IntFlag):
    SPDKL_DefaultLocation = 0
    SPDKL_CurrentUser = 1
    SPDKL_LocalMachine = 2
    SPDKL_CurrentConfig = 5


class SpeechGrammarRuleStateTransitionType(IntFlag):
    SGRSTTEpsilon = 0
    SGRSTTWord = 1
    SGRSTTRule = 2
    SGRSTTDictation = 3
    SGRSTTWildcard = 4
    SGRSTTTextBuffer = 5


class SPBOOKMARKOPTIONS(IntFlag):
    SPBO_NONE = 0
    SPBO_PAUSE = 1
    SPBO_AHEAD = 2
    SPBO_TIME_UNITS = 4


class SpeechTokenContext(IntFlag):
    STCInprocServer = 1
    STCInprocHandler = 2
    STCLocalServer = 4
    STCRemoteServer = 16
    STCAll = 23


class SpeechEmulationCompareFlags(IntFlag):
    SECFIgnoreCase = 1
    SECFIgnoreKanaType = 65536
    SECFIgnoreWidth = 131072
    SECFNoSpecialChars = 536870912
    SECFEmulateResult = 1073741824
    SECFDefault = 196609


class SPCONTEXTSTATE(IntFlag):
    SPCS_DISABLED = 0
    SPCS_ENABLED = 1


class DISPID_SpeechRecognizerStatus(IntFlag):
    DISPID_SRSAudioStatus = 1
    DISPID_SRSCurrentStreamPosition = 2
    DISPID_SRSCurrentStreamNumber = 3
    DISPID_SRSNumberOfActiveRules = 4
    DISPID_SRSClsidEngine = 5
    DISPID_SRSSupportedLanguages = 6


class SpeechVoiceEvents(IntFlag):
    SVEStartInputStream = 2
    SVEEndInputStream = 4
    SVEVoiceChange = 8
    SVEBookmark = 16
    SVEWordBoundary = 32
    SVEPhoneme = 64
    SVESentenceBoundary = 128
    SVEViseme = 256
    SVEAudioLevel = 512
    SVEPrivate = 32768
    SVEAllEvents = 33790


class SpeechRunState(IntFlag):
    SRSEDone = 1
    SRSEIsSpeaking = 2


class DISPID_SpeechRecoContext(IntFlag):
    DISPID_SRCRecognizer = 1
    DISPID_SRCAudioInInterferenceStatus = 2
    DISPID_SRCRequestedUIType = 3
    DISPID_SRCVoice = 4
    DISPID_SRAllowVoiceFormatMatchingOnNextSet = 5
    DISPID_SRCVoicePurgeEvent = 6
    DISPID_SRCEventInterests = 7
    DISPID_SRCCmdMaxAlternates = 8
    DISPID_SRCState = 9
    DISPID_SRCRetainedAudio = 10
    DISPID_SRCRetainedAudioFormat = 11
    DISPID_SRCPause = 12
    DISPID_SRCResume = 13
    DISPID_SRCCreateGrammar = 14
    DISPID_SRCCreateResultFromMemory = 15
    DISPID_SRCBookmark = 16
    DISPID_SRCSetAdaptationData = 17


class SpeechTokenShellFolder(IntFlag):
    STSF_AppData = 26
    STSF_LocalAppData = 28
    STSF_CommonAppData = 35
    STSF_FlagCreate = 32768


class DISPID_SpeechObjectToken(IntFlag):
    DISPID_SOTId = 1
    DISPID_SOTDataKey = 2
    DISPID_SOTCategory = 3
    DISPID_SOTGetDescription = 4
    DISPID_SOTSetId = 5
    DISPID_SOTGetAttribute = 6
    DISPID_SOTCreateInstance = 7
    DISPID_SOTRemove = 8
    DISPID_SOTGetStorageFileName = 9
    DISPID_SOTRemoveStorageFileName = 10
    DISPID_SOTIsUISupported = 11
    DISPID_SOTDisplayUI = 12
    DISPID_SOTMatchesAttributes = 13


class DISPID_SpeechDataKey(IntFlag):
    DISPID_SDKSetBinaryValue = 1
    DISPID_SDKGetBinaryValue = 2
    DISPID_SDKSetStringValue = 3
    DISPID_SDKGetStringValue = 4
    DISPID_SDKSetLongValue = 5
    DISPID_SDKGetlongValue = 6
    DISPID_SDKOpenKey = 7
    DISPID_SDKCreateKey = 8
    DISPID_SDKDeleteKey = 9
    DISPID_SDKDeleteValue = 10
    DISPID_SDKEnumKeys = 11
    DISPID_SDKEnumValues = 12


class SpeechVoicePriority(IntFlag):
    SVPNormal = 0
    SVPAlert = 1
    SVPOver = 2


class SPCATEGORYTYPE(IntFlag):
    SPCT_COMMAND = 0
    SPCT_DICTATION = 1
    SPCT_SLEEP = 2
    SPCT_SUB_COMMAND = 3
    SPCT_SUB_DICTATION = 4


class SpeechAudioState(IntFlag):
    SASClosed = 0
    SASStop = 1
    SASPause = 2
    SASRun = 3


class DISPID_SpeechObjectTokens(IntFlag):
    DISPID_SOTsCount = 1
    DISPID_SOTsItem = 0
    DISPID_SOTs_NewEnum = -4


class DISPIDSPRG(IntFlag):
    DISPID_SRGId = 1
    DISPID_SRGRecoContext = 2
    DISPID_SRGState = 3
    DISPID_SRGRules = 4
    DISPID_SRGReset = 5
    DISPID_SRGCommit = 6
    DISPID_SRGCmdLoadFromFile = 7
    DISPID_SRGCmdLoadFromObject = 8
    DISPID_SRGCmdLoadFromResource = 9
    DISPID_SRGCmdLoadFromMemory = 10
    DISPID_SRGCmdLoadFromProprietaryGrammar = 11
    DISPID_SRGCmdSetRuleState = 12
    DISPID_SRGCmdSetRuleIdState = 13
    DISPID_SRGDictationLoad = 14
    DISPID_SRGDictationUnload = 15
    DISPID_SRGDictationSetState = 16
    DISPID_SRGSetWordSequenceData = 17
    DISPID_SRGSetTextSelection = 18
    DISPID_SRGIsPronounceable = 19


class SpeechVoiceSpeakFlags(IntFlag):
    SVSFDefault = 0
    SVSFlagsAsync = 1
    SVSFPurgeBeforeSpeak = 2
    SVSFIsFilename = 4
    SVSFIsXML = 8
    SVSFIsNotXML = 16
    SVSFPersistXML = 32
    SVSFNLPSpeakPunc = 64
    SVSFParseSapi = 128
    SVSFParseSsml = 256
    SVSFParseAutodetect = 0
    SVSFNLPMask = 64
    SVSFParseMask = 384
    SVSFVoiceMask = 511
    SVSFUnusedFlags = -512


class SpeechAudioFormatType(IntFlag):
    SAFTDefault = -1
    SAFTNoAssignedFormat = 0
    SAFTText = 1
    SAFTNonStandardFormat = 2
    SAFTExtendedAudioFormat = 3
    SAFT8kHz8BitMono = 4
    SAFT8kHz8BitStereo = 5
    SAFT8kHz16BitMono = 6
    SAFT8kHz16BitStereo = 7
    SAFT11kHz8BitMono = 8
    SAFT11kHz8BitStereo = 9
    SAFT11kHz16BitMono = 10
    SAFT11kHz16BitStereo = 11
    SAFT12kHz8BitMono = 12
    SAFT12kHz8BitStereo = 13
    SAFT12kHz16BitMono = 14
    SAFT12kHz16BitStereo = 15
    SAFT16kHz8BitMono = 16
    SAFT16kHz8BitStereo = 17
    SAFT16kHz16BitMono = 18
    SAFT16kHz16BitStereo = 19
    SAFT22kHz8BitMono = 20
    SAFT22kHz8BitStereo = 21
    SAFT22kHz16BitMono = 22
    SAFT22kHz16BitStereo = 23
    SAFT24kHz8BitMono = 24
    SAFT24kHz8BitStereo = 25
    SAFT24kHz16BitMono = 26
    SAFT24kHz16BitStereo = 27
    SAFT32kHz8BitMono = 28
    SAFT32kHz8BitStereo = 29
    SAFT32kHz16BitMono = 30
    SAFT32kHz16BitStereo = 31
    SAFT44kHz8BitMono = 32
    SAFT44kHz8BitStereo = 33
    SAFT44kHz16BitMono = 34
    SAFT44kHz16BitStereo = 35
    SAFT48kHz8BitMono = 36
    SAFT48kHz8BitStereo = 37
    SAFT48kHz16BitMono = 38
    SAFT48kHz16BitStereo = 39
    SAFTTrueSpeech_8kHz1BitMono = 40
    SAFTCCITT_ALaw_8kHzMono = 41
    SAFTCCITT_ALaw_8kHzStereo = 42
    SAFTCCITT_ALaw_11kHzMono = 43
    SAFTCCITT_ALaw_11kHzStereo = 44
    SAFTCCITT_ALaw_22kHzMono = 45
    SAFTCCITT_ALaw_22kHzStereo = 46
    SAFTCCITT_ALaw_44kHzMono = 47
    SAFTCCITT_ALaw_44kHzStereo = 48
    SAFTCCITT_uLaw_8kHzMono = 49
    SAFTCCITT_uLaw_8kHzStereo = 50
    SAFTCCITT_uLaw_11kHzMono = 51
    SAFTCCITT_uLaw_11kHzStereo = 52
    SAFTCCITT_uLaw_22kHzMono = 53
    SAFTCCITT_uLaw_22kHzStereo = 54
    SAFTCCITT_uLaw_44kHzMono = 55
    SAFTCCITT_uLaw_44kHzStereo = 56
    SAFTADPCM_8kHzMono = 57
    SAFTADPCM_8kHzStereo = 58
    SAFTADPCM_11kHzMono = 59
    SAFTADPCM_11kHzStereo = 60
    SAFTADPCM_22kHzMono = 61
    SAFTADPCM_22kHzStereo = 62
    SAFTADPCM_44kHzMono = 63
    SAFTADPCM_44kHzStereo = 64
    SAFTGSM610_8kHzMono = 65
    SAFTGSM610_11kHzMono = 66
    SAFTGSM610_22kHzMono = 67
    SAFTGSM610_44kHzMono = 68


class DISPID_SpeechObjectTokenCategory(IntFlag):
    DISPID_SOTCId = 1
    DISPID_SOTCDefault = 2
    DISPID_SOTCSetId = 3
    DISPID_SOTCGetDataKey = 4
    DISPID_SOTCEnumerateTokens = 5


class DISPID_SpeechAudioFormat(IntFlag):
    DISPID_SAFType = 1
    DISPID_SAFGuid = 2
    DISPID_SAFGetWaveFormatEx = 3
    DISPID_SAFSetWaveFormatEx = 4


class DISPID_SpeechRecoContextEvents(IntFlag):
    DISPID_SRCEStartStream = 1
    DISPID_SRCEEndStream = 2
    DISPID_SRCEBookmark = 3
    DISPID_SRCESoundStart = 4
    DISPID_SRCESoundEnd = 5
    DISPID_SRCEPhraseStart = 6
    DISPID_SRCERecognition = 7
    DISPID_SRCEHypothesis = 8
    DISPID_SRCEPropertyNumberChange = 9
    DISPID_SRCEPropertyStringChange = 10
    DISPID_SRCEFalseRecognition = 11
    DISPID_SRCEInterference = 12
    DISPID_SRCERequestUI = 13
    DISPID_SRCERecognizerStateChange = 14
    DISPID_SRCEAdaptation = 15
    DISPID_SRCERecognitionForOtherContext = 16
    DISPID_SRCEAudioLevel = 17
    DISPID_SRCEEnginePrivate = 18


class DISPID_SpeechBaseStream(IntFlag):
    DISPID_SBSFormat = 1
    DISPID_SBSRead = 2
    DISPID_SBSWrite = 3
    DISPID_SBSSeek = 4


class SPPARTOFSPEECH(IntFlag):
    SPPS_NotOverriden = -1
    SPPS_Unknown = 0
    SPPS_Noun = 4096
    SPPS_Verb = 8192
    SPPS_Modifier = 12288
    SPPS_Function = 16384
    SPPS_Interjection = 20480
    SPPS_Noncontent = 24576
    SPPS_LMA = 28672
    SPPS_SuppressWord = 61440


class DISPID_SpeechAudio(IntFlag):
    DISPID_SAStatus = 200
    DISPID_SABufferInfo = 201
    DISPID_SADefaultFormat = 202
    DISPID_SAVolume = 203
    DISPID_SABufferNotifySize = 204
    DISPID_SAEventHandle = 205
    DISPID_SASetState = 206


class DISPID_SpeechMMSysAudio(IntFlag):
    DISPID_SMSADeviceId = 300
    DISPID_SMSALineId = 301
    DISPID_SMSAMMHandle = 302


class SpeechLoadOption(IntFlag):
    SLOStatic = 0
    SLODynamic = 1


class SPLEXICONTYPE(IntFlag):
    eLEXTYPE_USER = 1
    eLEXTYPE_APP = 2
    eLEXTYPE_VENDORLEXICON = 4
    eLEXTYPE_LETTERTOSOUND = 8
    eLEXTYPE_MORPHOLOGY = 16
    eLEXTYPE_RESERVED4 = 32
    eLEXTYPE_USER_SHORTCUT = 64
    eLEXTYPE_RESERVED6 = 128
    eLEXTYPE_RESERVED7 = 256
    eLEXTYPE_RESERVED8 = 512
    eLEXTYPE_RESERVED9 = 1024
    eLEXTYPE_RESERVED10 = 2048
    eLEXTYPE_PRIVATE1 = 4096
    eLEXTYPE_PRIVATE2 = 8192
    eLEXTYPE_PRIVATE3 = 16384
    eLEXTYPE_PRIVATE4 = 32768
    eLEXTYPE_PRIVATE5 = 65536
    eLEXTYPE_PRIVATE6 = 131072
    eLEXTYPE_PRIVATE7 = 262144
    eLEXTYPE_PRIVATE8 = 524288
    eLEXTYPE_PRIVATE9 = 1048576
    eLEXTYPE_PRIVATE10 = 2097152
    eLEXTYPE_PRIVATE11 = 4194304
    eLEXTYPE_PRIVATE12 = 8388608
    eLEXTYPE_PRIVATE13 = 16777216
    eLEXTYPE_PRIVATE14 = 33554432
    eLEXTYPE_PRIVATE15 = 67108864
    eLEXTYPE_PRIVATE16 = 134217728
    eLEXTYPE_PRIVATE17 = 268435456
    eLEXTYPE_PRIVATE18 = 536870912
    eLEXTYPE_PRIVATE19 = 1073741824
    eLEXTYPE_PRIVATE20 = -2147483648


class DISPID_SpeechFileStream(IntFlag):
    DISPID_SFSOpen = 100
    DISPID_SFSClose = 101


class DISPID_SpeechGrammarRule(IntFlag):
    DISPID_SGRAttributes = 1
    DISPID_SGRInitialState = 2
    DISPID_SGRName = 3
    DISPID_SGRId = 4
    DISPID_SGRClear = 5
    DISPID_SGRAddResource = 6
    DISPID_SGRAddState = 7


class DISPID_SpeechCustomStream(IntFlag):
    DISPID_SCSBaseStream = 100


class SpeechRecognizerState(IntFlag):
    SRSInactive = 0
    SRSActive = 1
    SRSActiveAlways = 2
    SRSInactiveWithPurge = 3


class SpeechFormatType(IntFlag):
    SFTInput = 0
    SFTSREngine = 1


class DISPID_SpeechMemoryStream(IntFlag):
    DISPID_SMSSetData = 100
    DISPID_SMSGetData = 101


class DISPID_SpeechAudioStatus(IntFlag):
    DISPID_SASFreeBufferSpace = 1
    DISPID_SASNonBlockingIO = 2
    DISPID_SASState = 3
    DISPID_SASCurrentSeekPosition = 4
    DISPID_SASCurrentDevicePosition = 5


class DISPID_SpeechGrammarRules(IntFlag):
    DISPID_SGRsCount = 1
    DISPID_SGRsDynamic = 2
    DISPID_SGRsAdd = 3
    DISPID_SGRsCommit = 4
    DISPID_SGRsCommitAndSave = 5
    DISPID_SGRsFindRule = 6
    DISPID_SGRsItem = 0
    DISPID_SGRs_NewEnum = -4


class SpeechVisemeFeature(IntFlag):
    SVF_None = 0
    SVF_Stressed = 1
    SVF_Emphasis = 2


class SpeechRuleState(IntFlag):
    SGDSInactive = 0
    SGDSActive = 1
    SGDSActiveWithAutoPause = 3
    SGDSActiveUserDelimited = 4


class SpeechBookmarkOptions(IntFlag):
    SBONone = 0
    SBOPause = 1


class SpeechRecognitionType(IntFlag):
    SRTStandard = 0
    SRTAutopause = 1
    SRTEmulated = 2
    SRTSMLTimeout = 4
    SRTExtendableParse = 8
    SRTReSent = 16


class SpeechInterference(IntFlag):
    SINone = 0
    SINoise = 1
    SINoSignal = 2
    SITooLoud = 3
    SITooQuiet = 4
    SITooFast = 5
    SITooSlow = 6


class DISPID_SpeechAudioBufferInfo(IntFlag):
    DISPID_SABIMinNotification = 1
    DISPID_SABIBufferSize = 2
    DISPID_SABIEventBias = 3


class SpeechVisemeType(IntFlag):
    SVP_0 = 0
    SVP_1 = 1
    SVP_2 = 2
    SVP_3 = 3
    SVP_4 = 4
    SVP_5 = 5
    SVP_6 = 6
    SVP_7 = 7
    SVP_8 = 8
    SVP_9 = 9
    SVP_10 = 10
    SVP_11 = 11
    SVP_12 = 12
    SVP_13 = 13
    SVP_14 = 14
    SVP_15 = 15
    SVP_16 = 16
    SVP_17 = 17
    SVP_18 = 18
    SVP_19 = 19
    SVP_20 = 20
    SVP_21 = 21


class DISPID_SpeechGrammarRuleState(IntFlag):
    DISPID_SGRSRule = 1
    DISPID_SGRSTransitions = 2
    DISPID_SGRSAddWordTransition = 3
    DISPID_SGRSAddRuleTransition = 4
    DISPID_SGRSAddSpecialTransition = 5


class DISPID_SpeechWaveFormatEx(IntFlag):
    DISPID_SWFEFormatTag = 1
    DISPID_SWFEChannels = 2
    DISPID_SWFESamplesPerSec = 3
    DISPID_SWFEAvgBytesPerSec = 4
    DISPID_SWFEBlockAlign = 5
    DISPID_SWFEBitsPerSample = 6
    DISPID_SWFEExtraData = 7


class DISPID_SpeechGrammarRuleStateTransitions(IntFlag):
    DISPID_SGRSTsCount = 1
    DISPID_SGRSTsItem = 0
    DISPID_SGRSTs_NewEnum = -4


class DISPID_SpeechGrammarRuleStateTransition(IntFlag):
    DISPID_SGRSTType = 1
    DISPID_SGRSTText = 2
    DISPID_SGRSTRule = 3
    DISPID_SGRSTWeight = 4
    DISPID_SGRSTPropertyName = 5
    DISPID_SGRSTPropertyId = 6
    DISPID_SGRSTPropertyValue = 7
    DISPID_SGRSTNextState = 8


class _SPAUDIOSTATE(IntFlag):
    SPAS_CLOSED = 0
    SPAS_STOP = 1
    SPAS_PAUSE = 2
    SPAS_RUN = 3


class SpeechWordPronounceable(IntFlag):
    SWPUnknownWordUnpronounceable = 0
    SWPUnknownWordPronounceable = 1
    SWPKnownWordPronounceable = 2


class DISPIDSPTSI(IntFlag):
    DISPIDSPTSI_ActiveOffset = 1
    DISPIDSPTSI_ActiveLength = 2
    DISPIDSPTSI_SelectionOffset = 3
    DISPIDSPTSI_SelectionLength = 4


class SpeechDiscardType(IntFlag):
    SDTProperty = 1
    SDTReplacement = 2
    SDTRule = 4
    SDTDisplayText = 8
    SDTLexicalForm = 16
    SDTPronunciation = 32
    SDTAudio = 64
    SDTAlternates = 128
    SDTAll = 255


class DISPID_SpeechRecoResult(IntFlag):
    DISPID_SRRRecoContext = 1
    DISPID_SRRTimes = 2
    DISPID_SRRAudioFormat = 3
    DISPID_SRRPhraseInfo = 4
    DISPID_SRRAlternates = 5
    DISPID_SRRAudio = 6
    DISPID_SRRSpeakAudio = 7
    DISPID_SRRSaveToMemory = 8
    DISPID_SRRDiscardResultInfo = 9


class SpeechDisplayAttributes(IntFlag):
    SDA_No_Trailing_Space = 0
    SDA_One_Trailing_Space = 2
    SDA_Two_Trailing_Spaces = 4
    SDA_Consume_Leading_Spaces = 8


class DISPID_SpeechXMLRecoResult(IntFlag):
    DISPID_SRRGetXMLResult = 10
    DISPID_SRRGetXMLErrorInfo = 11


class SPXMLRESULTOPTIONS(IntFlag):
    SPXRO_SML = 0
    SPXRO_Alternates_SML = 1


class SPRECOSTATE(IntFlag):
    SPRST_INACTIVE = 0
    SPRST_ACTIVE = 1
    SPRST_ACTIVE_ALWAYS = 2
    SPRST_INACTIVE_WITH_PURGE = 3
    SPRST_NUM_STATES = 4


class SPWAVEFORMATTYPE(IntFlag):
    SPWF_INPUT = 0
    SPWF_SRENGINE = 1


class SPSEMANTICFORMAT(IntFlag):
    SPSMF_SAPI_PROPERTIES = 0
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS = 1
    SPSMF_SRGS_SAPIPROPERTIES = 2
    SPSMF_UPS = 4
    SPSMF_SRGS_SEMANTICINTERPRETATION_W3C = 8


class DISPID_SpeechRecoResult2(IntFlag):
    DISPID_SRRSetTextFeedback = 12


class SPFILEMODE(IntFlag):
    SPFM_OPEN_READONLY = 0
    SPFM_OPEN_READWRITE = 1
    SPFM_CREATE = 2
    SPFM_CREATE_ALWAYS = 3
    SPFM_NUM_MODES = 4


class SPWORDTYPE(IntFlag):
    eWORDTYPE_ADDED = 1
    eWORDTYPE_DELETED = 2


class SPGRAMMARWORDTYPE(IntFlag):
    SPWT_DISPLAY = 0
    SPWT_LEXICAL = 1
    SPWT_PRONUNCIATION = 2
    SPWT_LEXICAL_NO_SPECIAL_CHARS = 3


class SPLOADOPTIONS(IntFlag):
    SPLO_STATIC = 0
    SPLO_DYNAMIC = 1


class SPRULESTATE(IntFlag):
    SPRS_INACTIVE = 0
    SPRS_ACTIVE = 1
    SPRS_ACTIVE_WITH_AUTO_PAUSE = 3
    SPRS_ACTIVE_USER_DELIMITED = 4


class SPWORDPRONOUNCEABLE(IntFlag):
    SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE = 0
    SPWP_UNKNOWN_WORD_PRONOUNCEABLE = 1
    SPWP_KNOWN_WORD_PRONOUNCEABLE = 2


class SPGRAMMARSTATE(IntFlag):
    SPGS_DISABLED = 0
    SPGS_ENABLED = 1
    SPGS_EXCLUSIVE = 3


class SPSHORTCUTTYPE(IntFlag):
    SPSHT_NotOverriden = -1
    SPSHT_Unknown = 0
    SPSHT_EMAIL = 4096
    SPSHT_OTHER = 8192
    SPPS_RESERVED1 = 12288
    SPPS_RESERVED2 = 16384
    SPPS_RESERVED3 = 20480
    SPPS_RESERVED4 = 61440


class SpeechEngineConfidence(IntFlag):
    SECLowConfidence = -1
    SECNormalConfidence = 0
    SECHighConfidence = 1


class SPVPRIORITY(IntFlag):
    SPVPRI_NORMAL = 0
    SPVPRI_ALERT = 1
    SPVPRI_OVER = 2


class SPEVENTENUM(IntFlag):
    SPEI_UNDEFINED = 0
    SPEI_START_INPUT_STREAM = 1
    SPEI_END_INPUT_STREAM = 2
    SPEI_VOICE_CHANGE = 3
    SPEI_TTS_BOOKMARK = 4
    SPEI_WORD_BOUNDARY = 5
    SPEI_PHONEME = 6
    SPEI_SENTENCE_BOUNDARY = 7
    SPEI_VISEME = 8
    SPEI_TTS_AUDIO_LEVEL = 9
    SPEI_TTS_PRIVATE = 15
    SPEI_MIN_TTS = 1
    SPEI_MAX_TTS = 15
    SPEI_END_SR_STREAM = 34
    SPEI_SOUND_START = 35
    SPEI_SOUND_END = 36
    SPEI_PHRASE_START = 37
    SPEI_RECOGNITION = 38
    SPEI_HYPOTHESIS = 39
    SPEI_SR_BOOKMARK = 40
    SPEI_PROPERTY_NUM_CHANGE = 41
    SPEI_PROPERTY_STRING_CHANGE = 42
    SPEI_FALSE_RECOGNITION = 43
    SPEI_INTERFERENCE = 44
    SPEI_REQUEST_UI = 45
    SPEI_RECO_STATE_CHANGE = 46
    SPEI_ADAPTATION = 47
    SPEI_START_SR_STREAM = 48
    SPEI_RECO_OTHER_CONTEXT = 49
    SPEI_SR_AUDIO_LEVEL = 50
    SPEI_SR_RETAINEDAUDIO = 51
    SPEI_SR_PRIVATE = 52
    SPEI_ACTIVE_CATEGORY_CHANGED = 53
    SPEI_RESERVED5 = 54
    SPEI_RESERVED6 = 55
    SPEI_MIN_SR = 34
    SPEI_MAX_SR = 55
    SPEI_RESERVED1 = 30
    SPEI_RESERVED2 = 33
    SPEI_RESERVED3 = 63


class DISPID_SpeechRecoResultTimes(IntFlag):
    DISPID_SRRTStreamTime = 1
    DISPID_SRRTLength = 2
    DISPID_SRRTTickCount = 3
    DISPID_SRRTOffsetFromStart = 4


class SpeechRecoEvents(IntFlag):
    SREStreamEnd = 1
    SRESoundStart = 2
    SRESoundEnd = 4
    SREPhraseStart = 8
    SRERecognition = 16
    SREHypothesis = 32
    SREBookmark = 64
    SREPropertyNumChange = 128
    SREPropertyStringChange = 256
    SREFalseRecognition = 512
    SREInterference = 1024
    SRERequestUI = 2048
    SREStateChange = 4096
    SREAdaptation = 8192
    SREStreamStart = 16384
    SRERecoOtherContext = 32768
    SREAudioLevel = 65536
    SREPrivate = 262144
    SREAllEvents = 393215


class SpeechRecoContextState(IntFlag):
    SRCS_Disabled = 0
    SRCS_Enabled = 1


class SpeechRetainedAudioOptions(IntFlag):
    SRAONone = 0
    SRAORetainAudio = 1


class DISPID_SpeechPhraseBuilder(IntFlag):
    DISPID_SPPBRestorePhraseFromMemory = 1


class SPVISEMES(IntFlag):
    SP_VISEME_0 = 0
    SP_VISEME_1 = 1
    SP_VISEME_2 = 2
    SP_VISEME_3 = 3
    SP_VISEME_4 = 4
    SP_VISEME_5 = 5
    SP_VISEME_6 = 6
    SP_VISEME_7 = 7
    SP_VISEME_8 = 8
    SP_VISEME_9 = 9
    SP_VISEME_10 = 10
    SP_VISEME_11 = 11
    SP_VISEME_12 = 12
    SP_VISEME_13 = 13
    SP_VISEME_14 = 14
    SP_VISEME_15 = 15
    SP_VISEME_16 = 16
    SP_VISEME_17 = 17
    SP_VISEME_18 = 18
    SP_VISEME_19 = 19
    SP_VISEME_20 = 20
    SP_VISEME_21 = 21


class DISPID_SpeechPhraseAlternate(IntFlag):
    DISPID_SPARecoResult = 1
    DISPID_SPAStartElementInResult = 2
    DISPID_SPANumberOfElementsInResult = 3
    DISPID_SPAPhraseInfo = 4
    DISPID_SPACommit = 5


class DISPID_SpeechPhraseAlternates(IntFlag):
    DISPID_SPAsCount = 1
    DISPID_SPAsItem = 0
    DISPID_SPAs_NewEnum = -4


class DISPID_SpeechPhraseInfo(IntFlag):
    DISPID_SPILanguageId = 1
    DISPID_SPIGrammarId = 2
    DISPID_SPIStartTime = 3
    DISPID_SPIAudioStreamPosition = 4
    DISPID_SPIAudioSizeBytes = 5
    DISPID_SPIRetainedSizeBytes = 6
    DISPID_SPIAudioSizeTime = 7
    DISPID_SPIRule = 8
    DISPID_SPIProperties = 9
    DISPID_SPIElements = 10
    DISPID_SPIReplacements = 11
    DISPID_SPIEngineId = 12
    DISPID_SPIEnginePrivateData = 13
    DISPID_SPISaveToMemory = 14
    DISPID_SPIGetText = 15
    DISPID_SPIGetDisplayAttributes = 16


class DISPID_SpeechPhraseElement(IntFlag):
    DISPID_SPEAudioTimeOffset = 1
    DISPID_SPEAudioSizeTime = 2
    DISPID_SPEAudioStreamOffset = 3
    DISPID_SPEAudioSizeBytes = 4
    DISPID_SPERetainedStreamOffset = 5
    DISPID_SPERetainedSizeBytes = 6
    DISPID_SPEDisplayText = 7
    DISPID_SPELexicalForm = 8
    DISPID_SPEPronunciation = 9
    DISPID_SPEDisplayAttributes = 10
    DISPID_SPERequiredConfidence = 11
    DISPID_SPEActualConfidence = 12
    DISPID_SPEEngineConfidence = 13


class DISPID_SpeechPhraseElements(IntFlag):
    DISPID_SPEsCount = 1
    DISPID_SPEsItem = 0
    DISPID_SPEs_NewEnum = -4


class DISPID_SpeechPhraseReplacement(IntFlag):
    DISPID_SPRDisplayAttributes = 1
    DISPID_SPRText = 2
    DISPID_SPRFirstElement = 3
    DISPID_SPRNumberOfElements = 4


class DISPID_SpeechPhraseReplacements(IntFlag):
    DISPID_SPRsCount = 1
    DISPID_SPRsItem = 0
    DISPID_SPRs_NewEnum = -4


class DISPID_SpeechPhraseProperty(IntFlag):
    DISPID_SPPName = 1
    DISPID_SPPId = 2
    DISPID_SPPValue = 3
    DISPID_SPPFirstElement = 4
    DISPID_SPPNumberOfElements = 5
    DISPID_SPPEngineConfidence = 6
    DISPID_SPPConfidence = 7
    DISPID_SPPParent = 8
    DISPID_SPPChildren = 9


class SPINTERFERENCE(IntFlag):
    SPINTERFERENCE_NONE = 0
    SPINTERFERENCE_NOISE = 1
    SPINTERFERENCE_NOSIGNAL = 2
    SPINTERFERENCE_TOOLOUD = 3
    SPINTERFERENCE_TOOQUIET = 4
    SPINTERFERENCE_TOOFAST = 5
    SPINTERFERENCE_TOOSLOW = 6
    SPINTERFERENCE_LATENCY_WARNING = 7
    SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN = 8
    SPINTERFERENCE_LATENCY_TRUNCATE_END = 9


class DISPID_SpeechPhraseProperties(IntFlag):
    DISPID_SPPsCount = 1
    DISPID_SPPsItem = 0
    DISPID_SPPs_NewEnum = -4


class DISPID_SpeechPhraseRule(IntFlag):
    DISPID_SPRuleName = 1
    DISPID_SPRuleId = 2
    DISPID_SPRuleFirstElement = 3
    DISPID_SPRuleNumberOfElements = 4
    DISPID_SPRuleParent = 5
    DISPID_SPRuleChildren = 6
    DISPID_SPRuleConfidence = 7
    DISPID_SPRuleEngineConfidence = 8


SPAUDIOSTATE = _SPAUDIOSTATE
SPSTREAMFORMATTYPE = SPWAVEFORMATTYPE


__all__ = [
    'ISpLexicon', 'SAFT11kHz16BitMono', 'DISPID_SRCEEndStream',
    'SPWORDPRONOUNCEABLE', 'DISPID_SpeechVoiceStatus',
    'DISPID_SPIAudioSizeBytes', 'DISPID_SOTs_NewEnum',
    'eLEXTYPE_RESERVED8', 'SAFT48kHz16BitStereo', 'SECLowConfidence',
    'DISPID_SPIEngineId', 'SAFT16kHz8BitStereo',
    'SGDSActiveWithAutoPause', 'SAFTADPCM_44kHzStereo',
    'SRTAutopause', 'DISPID_SpeechAudioBufferInfo',
    'DISPID_SASCurrentDevicePosition', 'DISPID_SVPause',
    'DISPID_SGRAddResource', 'DISPID_SPIGrammarId', 'SP_VISEME_9',
    'eLEXTYPE_PRIVATE12', 'STSF_CommonAppData', 'DISPID_SPAsItem',
    'SDA_Consume_Leading_Spaces', 'DISPID_SVSLastBookmarkId',
    'SAFT16kHz16BitStereo', 'SREAudioLevel', 'DISPID_SPISaveToMemory',
    'SpeechTokenContext', 'SpUnCompressedLexicon',
    'SPWP_UNKNOWN_WORD_PRONOUNCEABLE', 'DISPID_SPRuleConfidence',
    'DISPID_SOTSetId', 'eLEXTYPE_PRIVATE5', 'eLEXTYPE_PRIVATE20',
    'SPCONTEXTSTATE', 'SREPrivate', 'DISPID_SDKDeleteKey',
    'DISPID_SPACommit', 'DISPID_SRCVoicePurgeEvent',
    'DISPID_SpeechLexiconWord', 'ISpeechGrammarRuleState',
    'SPINTERFERENCE_NOISE', 'SpeechInterference', 'SITooSlow',
    'DISPID_SVWaitUntilDone', 'DISPID_SRCEPhraseStart',
    'DISPID_SGRAttributes', 'DISPID_SPERetainedSizeBytes',
    'SDKLDefaultLocation', 'ISpeechLexiconWord', 'SPPS_SuppressWord',
    'DISPID_SVAlertBoundary', 'SPSERIALIZEDPHRASE',
    'SVEEndInputStream', 'DISPID_SRCRecognizer', 'SVSFNLPSpeakPunc',
    'SAFT22kHz16BitMono', 'SAFT32kHz8BitMono',
    'DISPID_SRCERecognizerStateChange', 'DISPID_SPRulesCount',
    'SPSMF_SRGS_SEMANTICINTERPRETATION_W3C', 'SPEI_MIN_SR',
    'SRSEIsSpeaking', 'SAFTCCITT_ALaw_44kHzStereo', 'SVP_18',
    'DISPIDSPTSI', 'DISPID_SPIGetText', 'DISPID_SAStatus',
    'DISPID_SOTRemove', 'DISPID_SpeechLexiconPronunciation',
    'SPPS_LMA', 'SPEI_PROPERTY_STRING_CHANGE', 'SAFT12kHz16BitStereo',
    'SREInterference', 'DISPID_SPPParent', 'SpeechRuleAttributes',
    'eLEXTYPE_RESERVED7', 'SPFILEMODE', 'SVP_5',
    'DISPID_SpeechAudioStatus', 'SPBO_AHEAD',
    'SpeechWordPronounceable', 'DISPIDSPTSI_SelectionLength',
    'SPEI_ACTIVE_CATEGORY_CHANGED', 'ISpVoice', 'DISPID_SPRulesItem',
    'SREStreamEnd', 'SPAO_RETAIN_AUDIO', 'SAFTCCITT_uLaw_22kHzStereo',
    'DISPID_SRCBookmark', 'ISpeechPhraseElements',
    'SpeechAudioFormatType', 'SpeechRetainedAudioOptions',
    'SREFalseRecognition', 'ISpeechPhoneConverter',
    'DISPID_SOTCEnumerateTokens', 'STSF_AppData', 'SPEI_PHRASE_START',
    'DISPID_SLWPronunciations', 'DISPID_SRCState', 'SPEI_MIN_TTS',
    'DISPID_SLPLangId', 'DISPID_SWFEExtraData',
    'SPDKL_DefaultLocation', 'DISPID_SPIAudioSizeTime', 'SRTStandard',
    'SPSNoun', 'SPRST_NUM_STATES', 'SpInprocRecognizer',
    'SSSPTRelativeToEnd', 'SpeechTokenKeyAttributes',
    'DISPID_SRGCommit', 'DISPID_SRGCmdLoadFromObject', 'SDTAll',
    'SPRS_ACTIVE', 'SP_VISEME_16', 'ISpeechObjectTokenCategory',
    'SpeechVisemeType', 'DISPID_SVSInputSentencePosition',
    'DISPID_SGRSTNextState', 'DISPID_SLWs_NewEnum',
    'SpeechAudioProperties', 'DISPID_SGRsCommitAndSave',
    '_RemotableHandle', 'DISPID_SPIProperties', 'SpPhraseInfoBuilder',
    'DISPID_SLWsCount', 'SLOStatic', 'DISPID_SPPsItem',
    'SPPROPERTYINFO', 'DISPID_SRRTLength', 'SGRSTTRule',
    'SAFT44kHz16BitStereo', 'DISPID_SRSCurrentStreamPosition',
    'eLEXTYPE_PRIVATE11', 'SPRECOSTATE', 'IEnumString',
    'SPSHORTCUTPAIRLIST', 'DISPID_SVSVisemeId',
    'SpeechCategoryRecognizers', 'DISPID_SGRSTransitions',
    'DISPID_SOTDisplayUI', 'SPEI_SR_PRIVATE',
    'DISPID_SpeechPhraseBuilder', 'DISPID_SPEAudioTimeOffset',
    'SAFTCCITT_ALaw_8kHzMono', 'SPPS_Interjection', 'SpeechRuleState',
    'SPEI_TTS_AUDIO_LEVEL', 'DISPID_SRRTTickCount', 'DISPID_SBSWrite',
    'SAFT16kHz16BitMono', 'SAFTCCITT_uLaw_11kHzMono',
    'SPEI_RESERVED3', 'SVSFIsXML', 'SVEBookmark',
    'DISPID_SRCEAudioLevel', 'DISPID_SVAudioOutput',
    'SpCompressedLexicon', 'ISpNotifySource',
    'DISPID_SpeechLexiconProns', 'ISpeechObjectTokens',
    'DISPID_SPIAudioStreamPosition', 'typelib_path', 'SFTSREngine',
    'eLEXTYPE_PRIVATE2', 'SRERequestUI', 'DISPID_SRGetRecognizers',
    'SAFTCCITT_uLaw_44kHzStereo', 'Speech_Max_Word_Length',
    'DISPID_SDKOpenKey', 'SPCT_SLEEP', 'DISPID_SVSLastResult',
    'DISPID_SAVolume', 'eLEXTYPE_RESERVED10',
    'DISPID_SPAStartElementInResult', 'DISPID_SPEs_NewEnum',
    'SpeechCategoryAudioIn', 'DISPID_SPPNumberOfElements',
    'DISPID_SPRuleFirstElement', 'SAFT8kHz8BitStereo',
    'SpeechFormatType', 'SP_VISEME_8', 'SDTReplacement',
    'ISpeechXMLRecoResult', 'SAFTGSM610_44kHzMono',
    'DISPID_SRCCmdMaxAlternates', 'DISPID_SASCurrentSeekPosition',
    'SPINTERFERENCE_TOOSLOW', 'SP_VISEME_10', 'DISPID_SPILanguageId',
    'eLEXTYPE_PRIVATE1', 'SPPS_Unknown', 'LONG_PTR',
    'ISpeechCustomStream', 'DISPID_SFSClose', 'SpObjectTokenCategory',
    'SPGRAMMARWORDTYPE', 'SP_VISEME_5', 'SVP_13',
    'SpeechRegistryLocalMachineRoot', 'SpeechRunState',
    'SPPARTOFSPEECH', 'SREPropertyNumChange', 'DISPID_SPIStartTime',
    'DISPID_SRGRules', 'DISPID_SPIReplacements',
    'SAFTADPCM_11kHzMono', 'SGSExclusive', 'DISPID_SDKDeleteValue',
    'SRAInterpreter', 'DISPID_SVSPhonemeId', 'SAFT11kHz8BitMono',
    'SpMMAudioIn', 'ISpeechAudioBufferInfo', 'SPEI_TTS_PRIVATE',
    'SPEI_PROPERTY_NUM_CHANGE', 'SPPS_Verb',
    'DISPID_SPEActualConfidence', 'DISPID_SpeechGrammarRules',
    'SAFT8kHz16BitMono', 'DISPID_SLRemovePronunciationByPhoneIds',
    'SVP_12', 'SPAS_RUN', 'SAFTCCITT_ALaw_11kHzMono',
    'SGRSTTWildcard', 'DISPID_SPRDisplayAttributes',
    'SPEI_WORD_BOUNDARY', 'SLTUser', 'SpVoice',
    'DISPIDSPTSI_SelectionOffset', 'SpeechGrammarWordType',
    'DISPID_SGRs_NewEnum', 'SpShortcut', 'SVSFParseSsml',
    'SpeechAllElements', 'ISpeechVoice', 'DISPID_SFSOpen',
    'SRSInactive', 'ISpeechRecoResult', 'SVSFDefault',
    'SVSFlagsAsync', 'DISPID_SGRAddState', 'SPGS_ENABLED', 'SVP_2',
    'SPINTERFERENCE_TOOFAST', 'DISPID_SRGCmdSetRuleState',
    'DISPID_SpeechFileStream', 'SPAR_Unknown', 'SSFMCreateForWrite',
    'SP_VISEME_19', 'SPRST_INACTIVE_WITH_PURGE',
    'DISPID_SRRSpeakAudio', 'ISpeechLexiconWords',
    'DISPID_SVEStreamStart', 'STSF_FlagCreate', 'DISPID_SGRsFindRule',
    'eLEXTYPE_PRIVATE16', 'SDTRule', 'STCRemoteServer',
    'SSTTTextBuffer', 'SPVPRI_ALERT', 'ISpeechRecoResultTimes',
    'SPFM_NUM_MODES', 'DISPID_SRGId', 'ISpRecoContext2',
    'DISPID_SABufferInfo', 'SRAImport', 'SSFMOpenForRead',
    'SPEI_SR_BOOKMARK', 'DISPID_SVSInputWordLength',
    'DISPID_SPPBRestorePhraseFromMemory', 'SPAUDIOBUFFERINFO',
    'DISPID_SVEBookmark', 'DISPID_SPELexicalForm', 'SPPS_Noncontent',
    'SpeechPropertyResourceUsage', 'ISpeechPhraseProperty',
    'SPWT_LEXICAL', 'SVP_7', 'SDTPronunciation',
    'DISPID_SABIMinNotification', 'DISPID_SOTCSetId',
    'DISPID_SRCResume', 'ISpeechGrammarRuleStateTransition',
    'SPEI_RESERVED5', 'SpWaveFormatEx', 'DISPID_SASNonBlockingIO',
    'SPBINARYGRAMMAR', 'SAFTDefault', 'SpStream', 'SpeechMicTraining',
    'SP_VISEME_11', 'SECFDefault',
    'SpeechGrammarRuleStateTransitionType', 'DISPID_SGRsCommit',
    'DISPID_SpeechGrammarRuleState', 'ISpRecognizer', 'SPCS_ENABLED',
    'eLEXTYPE_PRIVATE15', 'SRTEmulated', 'ISpPhrase',
    'DISPID_SRCERecognition', 'SPINTERFERENCE_TOOLOUD',
    'DISPID_SPRuleEngineConfidence', 'SpLexicon',
    'DISPID_SRGCmdLoadFromProprietaryGrammar', 'SWTDeleted',
    'ISpRecoGrammar', 'DISPID_SRRTimes', 'SPSHT_EMAIL',
    'DISPID_SLPPartOfSpeech', 'SPEI_RECOGNITION', 'DISPID_SVVoice',
    'DISPID_SREmulateRecognition', 'DISPID_SGRsItem',
    'DISPID_SpeechXMLRecoResult', 'ISpGrammarBuilder',
    'SpeechDisplayAttributes', 'SpeechVisemeFeature',
    'DISPID_SRGetPropertyString', 'SECFNoSpecialChars',
    'DISPID_SVSInputSentenceLength', 'SASPause', 'ISpResourceManager',
    'ISpeechPhraseReplacement', 'STSF_LocalAppData',
    'ISpeechObjectToken', 'SPADAPTATIONRELEVANCE',
    'SPSMF_SAPI_PROPERTIES', 'SpeechAudioFormatGUIDWave',
    'SPCT_SUB_DICTATION', 'SDTAudio', 'ISpRecoCategory',
    'SPPHRASEELEMENT', 'DISPID_SpeechAudioFormat', 'SVPNormal',
    'DISPID_SpeechPhraseAlternate', 'SpeechEngineProperties',
    'SPLEXICONTYPE', 'SpStreamFormatConverter', 'DISPID_SLWWord',
    'SpeechStreamFileMode', 'ISpShortcut', 'DISPID_SPPName',
    'SVSFParseAutodetect', 'SpeechDictationTopicSpelling',
    'SPEI_SR_RETAINEDAUDIO', 'DISPID_SRGIsPronounceable',
    'ISpXMLRecoResult', 'SREStreamStart',
    'DISPID_SRCreateRecoContext', 'SpeechTokenShellFolder',
    'SPWF_SRENGINE', 'DISPID_SOTCGetDataKey', 'DISPID_SMSALineId',
    'ISpRecoContext', 'SPRS_ACTIVE_WITH_AUTO_PAUSE',
    'DISPID_SPRNumberOfElements', 'SPINTERFERENCE',
    'DISPID_SVGetVoices', 'DISPID_SDKGetStringValue', 'SPCT_COMMAND',
    'SpeechEngineConfidence', 'SWPUnknownWordPronounceable', 'SVP_17',
    'SPRST_ACTIVE_ALWAYS', 'ISpObjectToken', 'DISPID_SVRate',
    'ISpDataKey', 'DISPID_SDKGetlongValue', 'SPAO_NONE',
    'DISPID_SVSyncronousSpeakTimeout', 'DISPID_SDKSetLongValue',
    'SAFT48kHz8BitStereo', 'SPPS_Noun', 'SVP_8',
    'DISPID_SRRAudioFormat', 'DISPID_SPRuleChildren', 'SVEAudioLevel',
    'SPSNotOverriden', 'DISPID_SRAllowVoiceFormatMatchingOnNextSet',
    'SPCT_DICTATION', 'SAFT11kHz16BitStereo',
    'SpeechCategoryAudioOut', 'SREStateChange', 'DISPID_SLPSymbolic',
    'SPSERIALIZEDRESULT', 'SVEViseme', 'SAFTCCITT_uLaw_11kHzStereo',
    'DISPID_SAEventHandle', 'SDA_No_Trailing_Space',
    'DISPID_SRGSetTextSelection', 'SPSEMANTICERRORINFO',
    'SpMMAudioOut', 'DISPID_SRCESoundEnd', 'ISpeechFileStream',
    'DISPID_SPRuleNumberOfElements', 'SPPS_RESERVED1',
    'SAFTNoAssignedFormat', 'SpeechEmulationCompareFlags',
    'ISpeechTextSelectionInformation', 'SpeechTokenIdUserLexicon',
    'SpeechVoiceSpeakFlags', 'DISPID_SGRSTPropertyValue',
    'SVSFPurgeBeforeSpeak', '_SPAUDIOSTATE',
    'DISPID_SRRDiscardResultInfo', 'SPSEMANTICFORMAT',
    'DISPID_SRCSetAdaptationData', 'SVF_None', 'SPEI_HYPOTHESIS',
    'DISPID_SRCEEnginePrivate', 'DISPID_SMSGetData',
    'DISPID_SPEPronunciation', 'DISPID_SVEventInterests', 'SITooFast',
    'SpPhoneticAlphabetConverter', 'DISPID_SRSAudioStatus', 'SRARoot',
    'DISPID_SRGDictationLoad', 'SPSMF_UPS', 'DISPID_SBSSeek',
    'DISPID_SDKGetBinaryValue', 'SPWORDTYPE', 'SGRSTTEpsilon',
    'DISPID_SABufferNotifySize', 'DISPID_SLPsCount',
    'DISPID_SGRSTs_NewEnum', 'SpeechRecoEvents',
    'SPWORDPRONUNCIATION', 'Speech_Default_Weight',
    'SAFT22kHz8BitMono', 'SAFTExtendedAudioFormat',
    'DISPID_SOTRemoveStorageFileName', 'DISPID_SpeechObjectToken',
    'SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN', 'DISPID_SGRSRule',
    'ISpeechGrammarRuleStateTransitions', 'ISpeechMMSysAudio',
    'DISPID_SRCEBookmark', 'SGSDisabled', 'ISpRecognizer3',
    'ISpObjectTokenCategory', 'SPEVENTSOURCEINFO',
    'SpeechAudioFormatGUIDText', 'SVP_6', 'SGRSTTWord', 'SPEVENT',
    'eWORDTYPE_DELETED', 'SPEI_TTS_BOOKMARK',
    'DISPID_SLAddPronunciationByPhoneIds', 'DISPID_SGRSTRule',
    'DISPID_SVEPhoneme', 'SPINTERFERENCE_NOSIGNAL', 'SPPS_RESERVED4',
    'DISPID_SGRId', 'DISPID_SPEAudioStreamOffset',
    'DISPID_SpeechAudio', 'ISpeechAudioStatus', 'SVSFIsNotXML',
    'DISPID_SRCEFalseRecognition', 'SVEPrivate',
    'SPRECOCONTEXTSTATUS', 'SVP_1',
    'DISPID_SPANumberOfElementsInResult', 'SPCT_SUB_COMMAND',
    'SP_VISEME_2', 'DISPID_SAFSetWaveFormatEx',
    'Speech_Max_Pron_Length', 'eLEXTYPE_PRIVATE13', 'SPSLMA',
    'SPAR_Medium', 'DISPID_SRAudioInputStream', 'SPFM_OPEN_READONLY',
    'SPLO_DYNAMIC', 'STCAll', 'DISPID_SVSpeakCompleteEvent',
    'DISPID_SVSCurrentStreamNumber', 'DISPID_SpeechPhoneConverter',
    'SBONone', 'DISPID_SGRName', 'SpeechGrammarTagDictation',
    'DISPID_SPRules_NewEnum', 'ISpStreamFormat',
    'SpeechBookmarkOptions', 'DISPID_SpeechVoiceEvent',
    'DISPID_SPAsCount', 'DISPID_SPPValue',
    'SpTextSelectionInformation', 'DISPID_SVPriority',
    'DISPID_SpeechMMSysAudio', 'SAFT12kHz8BitStereo',
    'ISpeechRecognizer', 'SPLOADOPTIONS', 'STCInprocServer',
    'ISpRecognizer2', 'SPWF_INPUT', 'SAFT32kHz8BitStereo',
    'DISPID_SBSFormat', 'DISPID_SRRAlternates',
    'eLEXTYPE_VENDORLEXICON', 'DISPID_SPEAudioSizeTime', 'SAFTText',
    'eLEXTYPE_USER_SHORTCUT', 'SPPS_Function', 'SP_VISEME_1',
    'SPEI_SOUND_END', 'SAFTCCITT_ALaw_22kHzStereo', 'SPGRAMMARSTATE',
    'ISpSerializeState', 'SpeechCategoryPhoneConverters',
    'DISPID_SPPFirstElement', 'SRERecoOtherContext',
    'SAFTGSM610_22kHzMono', 'DISPID_SGRClear',
    'SPSMF_SRGS_SEMANTICINTERPRETATION_MS', 'SPRULE',
    'SAFT24kHz8BitStereo', 'DISPID_SpeechGrammarRuleStateTransitions',
    'DISPID_SRCEventInterests', 'SREHypothesis',
    'DISPID_SPPConfidence', 'SAFT48kHz8BitMono', 'SVP_3',
    'ISpeechRecoContext', 'DISPID_SpeechPhraseProperty',
    'SpeechRecognizerState', 'SAFT16kHz8BitMono',
    'DISPID_SWFEBitsPerSample', 'STCLocalServer',
    'DISPID_SMSADeviceId', 'SGDSActiveUserDelimited', 'SPEI_MAX_TTS',
    'DISPID_SVSRunningState', 'DISPID_SRCPause', 'DISPID_SRState',
    'SpeechRegistryUserRoot', 'DISPID_SRSCurrentStreamNumber',
    'SPRECOGNIZERSTATUS', 'eLEXTYPE_PRIVATE3', 'SpObjectToken',
    'SAFT8kHz8BitMono', 'SP_VISEME_17', 'DISPID_SGRsDynamic',
    'DISPID_SRCESoundStart', 'SVPOver', 'DISPID_SDKEnumKeys',
    'SVP_14', 'SPSHORTCUTTYPE', 'STCInprocHandler',
    'SAFTNonStandardFormat', 'SRAONone', 'DISPID_SPRText',
    'eLEXTYPE_PRIVATE17', 'Speech_StreamPos_RealTime',
    'ISpeechLexiconPronunciations', 'SSTTWildcard', 'DISPID_SRGState',
    'DISPID_SRCEStartStream', 'SWPKnownWordPronounceable',
    'DISPID_SRAudioInput', 'DISPID_SVGetAudioInputs',
    'DISPID_SpeechPhraseProperties', 'SINoSignal', 'SVP_15',
    'SAFTCCITT_uLaw_22kHzMono', 'SRSActiveAlways',
    'SpeechGrammarTagUnlimitedDictation',
    'DISPID_SOTMatchesAttributes', 'SASClosed',
    'DISPID_SRGCmdLoadFromFile', 'SPRS_INACTIVE', 'SpFileStream',
    'SAFT44kHz8BitStereo', 'SLTApp', 'DISPID_SOTIsUISupported',
    'SAFT44kHz8BitMono', 'eLEXTYPE_RESERVED6', 'eLEXTYPE_PRIVATE18',
    'ISpeechPhraseReplacements', 'DISPID_SRRTStreamTime',
    'SPEI_RECO_OTHER_CONTEXT', 'DISPID_SVStatus',
    'DISPID_SpeechPhraseElements', 'DISPID_SVSpeak',
    'DISPID_SRAllowAudioInputFormatChangesOnNextSet', 'SSTTDictation',
    'SPDKL_CurrentConfig', 'DISPID_SPRs_NewEnum',
    'DISPID_SRDisplayUI', 'SPSSuppressWord', 'DISPID_SPRsCount',
    'ISpPhraseAlt', 'DISPID_SPCPhoneToId',
    'DISPID_SpeechRecoResultTimes', 'SREAllEvents',
    'DISPID_SDKEnumValues', 'DISPID_SRSClsidEngine', 'SPSFunction',
    'DISPID_SRCEAdaptation', 'IStream', 'DISPID_SVEWord',
    'eLEXTYPE_APP', 'SpeechPropertyLowConfidenceThreshold',
    'DISPID_SVEVoiceChange', 'SVP_9', 'SSFMOpenReadWrite', 'SVPAlert',
    'SPEI_RESERVED6', 'ISpeechPhraseAlternates',
    'ISpeechPhraseAlternate', 'DISPID_SpeechObjectTokenCategory',
    'SPEI_INTERFERENCE', 'SpeechAudioState', 'SpeechVoiceEvents',
    'DISPID_SAFType', 'SGSEnabled', 'SRSActive',
    'DISPID_SpeechLexiconWords', 'SpMemoryStream', 'DISPID_SRProfile',
    'eLEXTYPE_RESERVED9', 'SPSTREAMFORMATTYPE', 'SPEI_MAX_SR',
    'DISPID_SGRInitialState', 'ISpeechAudio',
    'SAFTCCITT_uLaw_8kHzMono', 'ISpeechPhraseProperties',
    'ISpeechVoiceStatus', 'SINone', 'SVP_19',
    'DISPID_SpeechPhraseReplacement', 'ISpEventSource',
    'SP_VISEME_18', 'SpMMAudioEnum', 'SpInProcRecoContext',
    'DISPID_SpeechPhraseReplacements', 'DISPID_SRCEInterference',
    'DISPID_SpeechPhraseAlternates', 'SGPronounciation',
    'DISPID_SDKSetStringValue', 'SRCS_Disabled', 'eLEXTYPE_PRIVATE14',
    'DISPID_SpeechMemoryStream', 'DISPID_SpeechCustomStream',
    'ISpeechRecoResultDispatch', 'DISPID_SpeechPhraseInfo',
    'SPRECORESULTTIMES', '__MIDL___MIDL_itf_sapi_0000_0020_0001',
    'DISPID_SOTCDefault', 'DISPID_SOTGetStorageFileName',
    'SVSFVoiceMask', 'DISPID_SRRSaveToMemory',
    'SPINTERFERENCE_LATENCY_WARNING', 'DISPID_SRRAudio',
    'SPPS_Modifier', 'SPEVENTENUM', 'SPAS_PAUSE',
    'SpeechRecoProfileProperties', 'SPWT_DISPLAY', 'SPAUDIOSTATUS',
    'DISPID_SRRSetTextFeedback', 'SPEI_ADAPTATION', 'SPRST_ACTIVE',
    'DISPID_SVDisplayUI', 'DISPID_SRSNumberOfActiveRules',
    'SECFIgnoreKanaType', 'DISPID_SVSLastBookmark', 'DISPID_SOTCId',
    'SPEI_REQUEST_UI', '__MIDL___MIDL_itf_sapi_0000_0020_0002',
    'DISPID_SRSSupportedLanguages', 'DISPID_SMSAMMHandle',
    'tagSTATSTG', 'SPBO_NONE', 'DISPID_SPRuleParent',
    'DISPID_SLWsItem', 'SP_VISEME_15', 'SRESoundEnd',
    'DISPIDSPTSI_ActiveLength', 'DISPID_SRGCmdLoadFromMemory',
    'SRTSMLTimeout', 'SPGS_EXCLUSIVE', 'DISPID_SDKSetBinaryValue',
    'SP_VISEME_4', 'DISPID_SpeechDataKey',
    'SPWP_KNOWN_WORD_PRONOUNCEABLE', 'DISPID_SPEDisplayAttributes',
    'SpeechPropertyAdaptationOn', 'SWPUnknownWordUnpronounceable',
    'SWTAdded', 'DISPID_SRIsShared', 'SAFTADPCM_22kHzStereo',
    'eLEXTYPE_MORPHOLOGY', 'SPLO_STATIC', 'DISPID_SGRSTPropertyName',
    'DISPID_SRGRecoContext', 'SPAR_Low', 'SpAudioFormat', 'SVP_0',
    'SpeechWordType', 'DISPID_SRRGetXMLResult', 'SRTReSent',
    'SPINTERFERENCE_LATENCY_TRUNCATE_END', 'DISPID_SGRSTPropertyId',
    'DISPID_SBSRead', 'DISPID_SRRecognizer', 'SRAORetainAudio',
    'SP_VISEME_13', 'eLEXTYPE_PRIVATE4', 'SVP_11',
    'ISpeechRecoGrammar', 'DISPID_SVAudioOutputStream',
    'SECFIgnoreWidth', 'SVP_4', 'SPWAVEFORMATTYPE', 'SGLexical',
    'SpeechGrammarState', 'SVSFParseMask', 'SPWORDLIST',
    'DISPID_SPERequiredConfidence',
    'SpeechPropertyHighConfidenceThreshold', 'eLEXTYPE_PRIVATE10',
    'DISPID_SRCCreateGrammar', 'SREAdaptation', 'ISpeechGrammarRules',
    'DISPIDSPTSI_ActiveOffset', 'SPEI_RECO_STATE_CHANGE',
    'ISpMMSysAudio', 'WAVEFORMATEX', 'SFTInput', 'SpCustomStream',
    'SPEI_PHONEME', 'DISPID_SABIEventBias', 'SGDisplay',
    'SAFTADPCM_44kHzMono', 'DISPID_SVEEnginePrivate', 'SPXRO_SML',
    'SINoise', 'DISPID_SPCIdToPhone', 'ISpeechWaveFormatEx',
    'SPWORDPRONUNCIATIONLIST', 'SECHighConfidence',
    'SpeechPartOfSpeech', 'ISpeechPhraseRules', 'DISPID_SPEsItem',
    'DISPID_SRStatus', 'DISPID_SCSBaseStream', 'SVSFIsFilename',
    'Library', 'SDTProperty', 'SPPHRASEREPLACEMENT',
    'DISPID_SRCEPropertyStringChange', 'SP_VISEME_14', 'SITooLoud',
    'DISPID_SVEAudioLevel', 'SpeechDiscardType',
    'DISPID_SpeechRecoResult2', 'SPSHT_Unknown', 'ISpEventSink',
    'DISPID_SVResume', 'SAFTGSM610_11kHzMono',
    'SpeechDataKeyLocation', 'ISpeechPhraseRule',
    'DISPID_SpeechObjectTokens', 'SDKLLocalMachine',
    'DISPID_SRCERequestUI', 'SDTLexicalForm', 'ISpRecoGrammar2',
    'SPAS_STOP', 'DISPID_SVESentenceBoundary', 'SRESoundStart',
    'DISPIDSPRG', 'ISpeechLexicon', 'SAFT22kHz16BitStereo',
    'SAFTADPCM_22kHzMono', 'SPRST_INACTIVE', 'DISPID_SRCVoice',
    'DISPID_SRCCreateResultFromMemory', 'SPSMF_SRGS_SAPIPROPERTIES',
    'DISPID_SLWLangId', 'DISPID_SLPPhoneIds',
    'DISPID_SpeechWaveFormatEx', 'ISpeechPhraseInfo',
    'DISPID_SRRRecoContext', 'SREPhraseStart', 'DISPID_SVEStreamEnd',
    'ISpNotifySink', 'SPEI_FALSE_RECOGNITION', 'DISPID_SDKCreateKey',
    'ISpStreamFormatConverter', 'DISPID_SLPType',
    'DISPID_SVSInputWordPosition', 'SVP_20',
    'DISPID_SpeechRecoResult', 'SpeechCategoryRecoProfiles',
    'SPEI_SENTENCE_BOUNDARY', 'DISPID_SGRSTType', 'SPPHRASEPROPERTY',
    'SPRS_ACTIVE_USER_DELIMITED', 'SpeechTokenKeyFiles',
    'SPBOOKMARKOPTIONS', 'DISPID_SPCLangId', 'ISpPhoneConverter',
    'DISPID_SGRSAddWordTransition', 'SAFT24kHz8BitMono',
    'DISPID_SRIsUISupported', 'DISPID_SPERetainedStreamOffset',
    'eWORDTYPE_ADDED', 'SPWORD', 'SECFEmulateResult', 'SVSFParseSapi',
    'DISPID_SPEDisplayText', 'ISpeechPhraseElement', 'SVSFPersistXML',
    'DISPID_SOTsCount', 'SRADefaultToActive', 'DISPID_SGRSTWeight',
    'DISPID_SVAllowAudioOuputFormatChangesOnNextSet',
    'SPDKL_CurrentUser', 'SSSPTRelativeToStart', 'SPBO_PAUSE',
    'DISPID_SGRSTsCount', 'SpSharedRecoContext',
    'SPEI_END_INPUT_STREAM', 'DISPID_SRRTOffsetFromStart',
    'DISPID_SpeechBaseStream', 'DISPID_SASFreeBufferSpace',
    'IInternetSecurityManager', 'SAFTADPCM_11kHzStereo',
    'SpeechVoicePriority', 'SpeechPropertyNormalConfidenceThreshold',
    'DISPID_SRSetPropertyNumber', 'SpeechAudioVolume',
    'SAFT22kHz8BitStereo', 'DISPID_SpeechRecoContextEvents',
    'ISpPhoneticAlphabetSelection', 'DISPID_SPPsCount',
    'DISPID_SVGetAudioOutputs', 'DISPID_SPEAudioSizeBytes',
    'SPSInterjection', 'ISpeechBaseStream',
    'DISPID_SpeechRecoContext', 'SpeechLoadOption', 'SASRun',
    'SAFT11kHz8BitStereo', 'SPSModifier', 'SRERecognition',
    'DISPID_SOTGetAttribute', 'ISpRecoResult', 'DISPID_SLPsItem',
    'SAFTADPCM_8kHzStereo', 'SRSInactiveWithPurge',
    'SDKLCurrentConfig', 'SPEI_RESERVED2', 'ISpeechResourceLoader',
    'DISPID_SRCRetainedAudioFormat', 'SpNotifyTranslator',
    'DISPID_SVSkip', 'SPAS_CLOSED', 'SPSHORTCUTPAIR', 'ISpStream',
    'tagSPPROPERTYINFO', 'DISPID_SOTCategory', 'SpResourceManager',
    'DISPID_SVGetProfiles', 'SPFM_OPEN_READWRITE',
    'eLEXTYPE_LETTERTOSOUND', 'SAFT32kHz16BitStereo', 'SPEI_VISEME',
    'SpeechCategoryVoices', 'ISpProperties', 'DISPID_SLWType',
    'SAFT12kHz8BitMono', 'DISPID_SWFEFormatTag', 'ISpObjectWithToken',
    'DISPID_SLGetPronunciations', 'SSSPTRelativeToCurrentPosition',
    'SRTExtendableParse', 'DISPID_SOTDataKey', 'SRATopLevel',
    'DISPID_SVEViseme', 'SVEVoiceChange', 'DISPID_SWFEBlockAlign',
    'ISpeechRecoResult2', 'SVEAllEvents', 'DISPID_SPAs_NewEnum',
    'DISPID_SLGetGenerationChange', 'eLEXTYPE_PRIVATE19',
    'DISPID_SPPEngineConfidence', 'DISPID_SPIGetDisplayAttributes',
    'SPBO_TIME_UNITS', 'DISPID_SADefaultFormat',
    'SAFTTrueSpeech_8kHz1BitMono', 'eLEXTYPE_RESERVED4', 'SVP_21',
    'DISPID_SWFESamplesPerSec', 'tagSPTEXTSELECTIONINFO',
    'ISpeechGrammarRule', 'SP_VISEME_20', 'SP_VISEME_12',
    'DISPID_SLPs_NewEnum', 'SpSharedRecognizer',
    'SpeechVoiceCategoryTTSRate', 'SPPS_NotOverriden',
    'SpNullPhoneConverter', 'ISpeechDataKey', 'SPXRO_Alternates_SML',
    'DISPID_SPRsItem', 'DISPID_SRCAudioInInterferenceStatus',
    'DISPID_SPPs_NewEnum', 'SPVPRI_NORMAL',
    'DISPID_SRGCmdLoadFromResource', 'DISPID_SGRSAddRuleTransition',
    'SVSFNLPMask', 'SPFM_CREATE', 'SPPHRASE', 'SGDSActive',
    'SP_VISEME_6', 'SPAR_High', 'SAFT48kHz16BitMono',
    'DISPID_SMSSetData', 'DISPID_SRGCmdSetRuleIdState',
    'SVEStartInputStream', 'DISPID_SWFEChannels', 'SpeechLexiconType',
    'SpeechAddRemoveWord', 'SpeechTokenValueCLSID',
    'SPEI_SR_AUDIO_LEVEL', 'DISPID_SASetState', 'SPAUDIOSTATE',
    'SPEI_START_SR_STREAM', 'DISPID_SRRPhraseInfo',
    'SPEI_SOUND_START', 'SPVPRIORITY', 'SVSFUnusedFlags',
    'DISPID_SPRFirstElement', '__MIDL_IWinTypes_0009', 'SITooQuiet',
    'SAFTCCITT_ALaw_11kHzStereo', 'DISPID_SLRemovePronunciation',
    'ISpNotifyTranslator', 'SREPropertyStringChange',
    'DISPID_SRGReset', 'SPINTERFERENCE_TOOQUIET', 'SPEI_VOICE_CHANGE',
    'SECFIgnoreCase', 'DISPID_SRGSetWordSequenceData',
    'SPDATAKEYLOCATION', 'SVP_16', 'SRADynamic',
    'ISpeechLexiconPronunciation', 'DISPID_SVSpeakStream',
    'ISpeechMemoryStream', 'DISPID_SPPChildren',
    'SDA_Two_Trailing_Spaces', 'DISPID_SPIElements',
    'SGRSTTTextBuffer', 'DISPID_SpeechGrammarRule',
    'DISPID_SpeechRecognizerStatus', 'SPWT_PRONUNCIATION',
    'SPTEXTSELECTIONINFO', 'DISPID_SOTCreateInstance', 'SPSUnknown',
    'DISPID_SVSLastStreamNumberQueued', '_ISpeechRecoContextEvents',
    'DISPID_SpeechRecognizer', 'SGRSTTDictation',
    'SAFT32kHz16BitMono', 'DISPID_SGRSTsItem', 'SDTDisplayText',
    'SPINTERFERENCE_NONE', 'SECNormalConfidence',
    'SAFT24kHz16BitMono', 'SAFTADPCM_8kHzMono', 'DISPID_SVVolume',
    'SPWT_LEXICAL_NO_SPECIAL_CHARS', 'SPCATEGORYTYPE',
    'ISpeechPhraseInfoBuilder', 'SPCS_DISABLED',
    'SpeechRecoContextState', 'DISPID_SpeechPhraseElement',
    'DISPID_SLGetWords', 'DISPID_SRCEHypothesis', 'DISPID_SGRsCount',
    'DISPID_SPIRule', 'DISPID_SRCRequestedUIType',
    'ISpeechAudioFormat', 'DISPID_SAFGetWaveFormatEx',
    'IEnumSpObjectTokens', 'SPFM_CREATE_ALWAYS', 'SVP_10',
    'SPPS_RESERVED2', 'eLEXTYPE_PRIVATE6', 'DISPID_SpeechPhraseRule',
    'SLODynamic', 'SP_VISEME_3', 'DISPID_SRGDictationSetState',
    'SPAUDIOOPTIONS', 'DISPID_SGRSAddSpecialTransition', 'UINT_PTR',
    'SAFTCCITT_uLaw_8kHzStereo', 'SAFTGSM610_8kHzMono', 'SPVPRI_OVER',
    'DISPID_SABIBufferSize', 'DISPID_SRRGetXMLErrorInfo',
    'SPEI_UNDEFINED', 'SP_VISEME_0', 'DISPID_SASState', 'ISpAudio',
    'SpeechGrammarTagWildcard', 'SpeechVoiceSkipTypeSentence',
    'SAFT8kHz16BitStereo', 'DISPID_SRCERecognitionForOtherContext',
    'eLEXTYPE_USER', 'DISPID_SPAPhraseInfo', 'SAFT44kHz16BitMono',
    'SAFTCCITT_ALaw_8kHzStereo', 'DISPID_SLGenerationId',
    'SGDSInactive', 'DISPID_SpeechVoice', 'DISPID_SOTsItem',
    'SPSHT_OTHER', 'SpeechSpecialTransitionType', 'SPVISEMES',
    'ISpeechRecognizerStatus', 'SPSVerb',
    'SpeechPropertyComplexResponseSpeed', 'SVEWordBoundary',
    'DISPID_SpeechGrammarRuleStateTransition', 'DISPID_SPARecoResult',
    'SpeechStreamSeekPositionType', 'Speech_StreamPos_Asap',
    'DISPID_SRCEPropertyNumberChange', 'SPRULESTATE',
    'DISPID_SLAddPronunciation', 'eLEXTYPE_PRIVATE7', 'SBOPause',
    'IInternetSecurityMgrSite', 'DISPID_SPRuleId', 'SRAExport',
    'SPSHT_NotOverriden', 'SAFTCCITT_ALaw_44kHzMono', 'SREBookmark',
    'DISPID_SPEEngineConfidence', 'DISPID_SWFEAvgBytesPerSec',
    'DISPID_SRSetPropertyString', 'SAFTCCITT_ALaw_22kHzMono',
    'SPVOICESTATUS', 'SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE',
    'SRCS_Enabled', 'SPEI_END_SR_STREAM', 'SVESentenceBoundary',
    'DISPID_SRCRetainedAudio', 'DISPID_SRGetPropertyNumber',
    'DISPID_SPIEnginePrivateData', 'DISPID_SpeechLexicon',
    'SVF_Stressed', 'SGLexicalNoSpecialChars', 'DISPID_SRGetFormat',
    'SAFT24kHz16BitStereo', 'SAFTCCITT_uLaw_44kHzMono', 'SASStop',
    'DISPID_SpeechPhraseRules', 'SPEI_RESERVED1',
    'SDA_One_Trailing_Space', 'eLEXTYPE_PRIVATE9', 'DISPID_SGRsAdd',
    'DISPID_SPEsCount', 'DISPID_SPRuleName',
    'SpeechCategoryAppLexicons', 'SP_VISEME_21',
    'SpeechPropertyResponseSpeed', 'SVEPhoneme', 'SpeechTokenKeyUI',
    'SPPS_RESERVED3', 'DISPID_SVIsUISupported', 'SPPHRASERULE',
    'DISPID_SAFGuid', 'SSFMCreate', '_ISpeechVoiceEvents',
    'SPEI_START_INPUT_STREAM', 'DISPID_SPIRetainedSizeBytes',
    'DISPID_SPPId', 'ISpPhoneticAlphabetConverter',
    'SpeechUserTraining', 'DISPID_SOTId', 'DISPID_SOTGetDescription',
    'SPGS_DISABLED', 'SAFT12kHz16BitMono', 'SpPhoneConverter',
    'SDKLCurrentUser', 'SVF_Emphasis', 'DISPID_SGRSTText',
    'eLEXTYPE_PRIVATE8', 'SPXMLRESULTOPTIONS', 'SDTAlternates',
    'SP_VISEME_7', 'SRSEDone', 'DISPID_SRGDictationUnload',
    'SpeechRecognitionType', 'SPDKL_LocalMachine'
]

