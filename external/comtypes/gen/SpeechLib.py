from enum import IntFlag

import comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 as __wrapper_module__
from comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 import (
    DISPID_SRCEHypothesis, SPBO_AHEAD, DISPID_SVGetProfiles,
    ISpeechRecoResult, SPINTERFERENCE_LATENCY_WARNING, SP_VISEME_8,
    eLEXTYPE_RESERVED10, SPEI_PHONEME, SVEWordBoundary, SBONone,
    DISPID_SRAudioInputStream, DISPID_SPERetainedStreamOffset,
    DISPID_SPIStartTime, SPFM_CREATE_ALWAYS, SVSFParseMask,
    SpNotifyTranslator, IInternetSecurityManager, Library,
    DISPID_SDKOpenKey, ISpeechAudioFormat, eLEXTYPE_PRIVATE13,
    ISpRecoContext, DISPID_SDKSetLongValue,
    DISPID_SRRTOffsetFromStart, ISpObjectTokenCategory,
    eLEXTYPE_PRIVATE5, ISpeechPhraseAlternates, SPVPRI_OVER,
    DISPID_SGRSRule, DISPID_SPCLangId, IEnumString, SPVPRI_ALERT,
    SVEEndInputStream, SPEVENTSOURCEINFO, SVP_5,
    SWPUnknownWordUnpronounceable, DISPID_SLGetWords, SVP_0,
    DISPID_SRState, SVSFIsXML, SpeechTokenValueCLSID, SVP_11,
    SGRSTTWord, ISpPhoneticAlphabetSelection, SVP_3,
    ISpeechPhraseRule, STSF_FlagCreate, DISPID_SVRate,
    DISPID_SOTCreateInstance, DISPID_SRGCmdSetRuleState, SVP_10,
    SPSModifier, DISPID_SOTCSetId, STSF_AppData, DISPID_SBSWrite,
    DISPID_SPIRetainedSizeBytes, SPBO_NONE, SpCompressedLexicon,
    __MIDL___MIDL_itf_sapi_0000_0020_0002, SDTAudio, ISpStream,
    SASStop, SPCT_SUB_DICTATION, Speech_Default_Weight,
    SRADefaultToActive, SpeechRegistryLocalMachineRoot, HRESULT,
    DISPID_SPPEngineConfidence, SRAInterpreter, eLEXTYPE_PRIVATE9,
    SPSSuppressWord, ISpRecognizer2, SPXRO_SML, eLEXTYPE_PRIVATE1,
    SRESoundStart, DISPID_SRAudioInput, SAFT22kHz8BitMono,
    DISPID_SOTsItem, SLTUser, SVEStartInputStream,
    ISpeechObjectTokens, SVP_9, SAFTADPCM_8kHzStereo,
    SSSPTRelativeToStart, ISpeechRecognizerStatus,
    DISPID_SVSyncronousSpeakTimeout, SGDSActiveUserDelimited,
    Speech_StreamPos_Asap, DISPID_SRCEEndStream, STCInprocHandler,
    SPEI_PROPERTY_STRING_CHANGE, ISpRecognizer,
    DISPID_SPRFirstElement, SPPROPERTYINFO,
    DISPID_SPEEngineConfidence, DISPID_SAFGetWaveFormatEx,
    SPEI_INTERFERENCE, SPWORDPRONUNCIATIONLIST, STCAll, SpFileStream,
    eLEXTYPE_PRIVATE4, DISPID_SFSClose, SAFT16kHz16BitMono,
    SPEI_SR_RETAINEDAUDIO, SRERequestUI, ISpeechPhraseReplacements,
    SREStreamStart, SRCS_Enabled, DISPID_SGRs_NewEnum,
    SpeechDictationTopicSpelling, DISPID_SGRsAdd, SECFIgnoreWidth,
    SPSHT_NotOverriden, SAFTCCITT_uLaw_44kHzMono,
    DISPID_SVGetAudioOutputs, DISPMETHOD, SVP_7, SREPrivate,
    SpWaveFormatEx, SPPS_RESERVED4, DISPID_SGRSTPropertyName,
    SVSFPurgeBeforeSpeak, DISPID_SVSPhonemeId, DISPID_SRCEBookmark,
    SPEI_FALSE_RECOGNITION, SWTAdded, SpeechTokenIdUserLexicon,
    ISpeechPhraseInfoBuilder, DISPID_SRGRecoContext,
    DISPID_SPIProperties, ISpeechRecoGrammar, SPEI_WORD_BOUNDARY,
    DISPID_SVAudioOutput, SVEBookmark, _check_version, DISPID_SOTId,
    SGRSTTDictation, DISPID_SGRSTsCount, DISPID_SPISaveToMemory,
    ISpeechFileStream, SPRST_NUM_STATES, SPINTERFERENCE_TOOQUIET,
    SPPS_Verb, SPPS_Interjection, DISPID_SVSLastBookmark, SPWORD,
    DISPID_SOTMatchesAttributes, SREFalseRecognition, SpVoice,
    SREInterference, DISPID_SRCEPhraseStart, SRAONone,
    ISpeechResourceLoader, SAFT22kHz16BitStereo,
    DISPID_SOTCGetDataKey, SPGS_ENABLED, DISPID_SRCEventInterests,
    SVP_15, DISPID_SAStatus, SGSEnabled, SDKLDefaultLocation,
    STSF_LocalAppData, DISPID_SRGCommit,
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS, SpeechAudioProperties,
    SECFEmulateResult, SpMemoryStream, CoClass, ISpEventSink,
    SP_VISEME_16, SPWORDLIST, DISPID_SPIAudioSizeBytes,
    DISPID_SVESentenceBoundary, DISPID_SPPName,
    DISPID_SOTRemoveStorageFileName, DISPID_SWFEExtraData,
    DISPID_SPPsCount, SP_VISEME_13, SAFT12kHz16BitStereo,
    DISPID_SGRSTPropertyValue, SPRST_ACTIVE_ALWAYS,
    DISPID_SRRGetXMLErrorInfo, ISpeechCustomStream,
    DISPID_SVSCurrentStreamNumber, SVPAlert, SAFTCCITT_ALaw_44kHzMono,
    DISPID_SGRAttributes, SPRECOGNIZERSTATUS, ISpShortcut,
    SPEI_SOUND_START, DISPID_SAVolume, SRADynamic,
    SAFTGSM610_11kHzMono, DISPID_SRCBookmark,
    ISpeechPhraseReplacement, ISpStreamFormat, SLTApp, SGDSInactive,
    DISPID_SLPPartOfSpeech, SECNormalConfidence, SAFT24kHz16BitMono,
    DISPID_SVEWord, SAFT32kHz8BitMono, SP_VISEME_9,
    DISPID_SABIMinNotification, SVP_20, DISPID_SPIReplacements,
    SPBO_TIME_UNITS, DISPID_SPPChildren, SPWT_PRONUNCIATION,
    ISpeechMemoryStream, SVSFVoiceMask, DISPID_SDKGetBinaryValue,
    _lcid, DISPID_SVSInputWordPosition, SpeechCategoryAppLexicons,
    DISPID_SGRId, SPSHORTCUTPAIRLIST, SASClosed,
    ISpeechObjectTokenCategory, DISPIDSPTSI_SelectionOffset,
    DISPID_SVResume, DISPID_SGRSTRule, DISPID_SLWsCount, SPEI_VISEME,
    helpstring, SRTStandard, SAFTADPCM_11kHzStereo, DISPID_SLPsItem,
    SPDKL_DefaultLocation, SPEI_START_INPUT_STREAM, SAFT24kHz8BitMono,
    SPINTERFERENCE_NOSIGNAL, SVEPrivate, SpeechCategoryAudioIn,
    SECFIgnoreCase, IServiceProvider, SPEI_SENTENCE_BOUNDARY,
    DISPID_SGRsItem, SPINTERFERENCE_TOOFAST, ISpEventSource,
    DISPID_SRRecognizer, DISPID_SGRsCommitAndSave, SGRSTTTextBuffer,
    DISPID_SBSRead, DISPID_SVEPhoneme, SPEI_SR_PRIVATE, SVSFNLPMask,
    DISPID_SPIElements, SAFTCCITT_ALaw_44kHzStereo,
    SpSharedRecoContext, DISPID_SRCVoice, SBOPause,
    SpeechGrammarTagWildcard, DISPID_SPPId, SVP_4,
    SPRS_ACTIVE_WITH_AUTO_PAUSE, eLEXTYPE_APP, SpeechCategoryVoices,
    SVF_Emphasis, DISPID_SDKSetBinaryValue, DISPID_SVStatus,
    DISPID_SRCEStartStream, SPRS_ACTIVE, SpMMAudioOut,
    ISpeechPhraseElements, ISpXMLRecoResult, SDA_No_Trailing_Space,
    SVEPhoneme, SREStreamEnd, SAFTADPCM_22kHzMono,
    DISPID_SWFEFormatTag, DISPID_SAFType, SPDKL_CurrentConfig,
    SPSMF_SAPI_PROPERTIES, SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE,
    DISPID_SMSGetData, SpPhoneticAlphabetConverter, DISPID_SPPParent,
    ISpeechPhoneConverter, DISPID_SRRGetXMLResult, DISPID_SPPsItem,
    SAFT12kHz8BitStereo, SRTReSent,
    SpeechPropertyLowConfidenceThreshold, DISPID_SRGCmdLoadFromObject,
    SAFT48kHz8BitMono, DISPID_SRGCmdSetRuleIdState,
    SAFTADPCM_8kHzMono, SVSFParseSsml, SpObjectToken,
    SREPropertyStringChange, SAFT8kHz8BitStereo, SP_VISEME_6,
    ISpeechBaseStream, SP_VISEME_4, SRSInactiveWithPurge,
    DISPID_SRCRequestedUIType, DISPID_SVPriority, SPEI_HYPOTHESIS,
    DISPID_SLWWord, SASRun, DISPID_SPRuleNumberOfElements,
    DISPID_SPAsItem, SP_VISEME_12, SPEI_MIN_SR, DISPID_SPPs_NewEnum,
    SDKLCurrentConfig, _ISpeechVoiceEvents, SAFTExtendedAudioFormat,
    DISPID_SBSFormat, SP_VISEME_17, DISPID_SRCRecognizer,
    DISPID_SPRules_NewEnum, DISPID_SPIAudioStreamPosition,
    DISPID_SPEAudioSizeBytes, SpeechRecoProfileProperties,
    tagSPTEXTSELECTIONINFO, DISPID_SVGetVoices, ISpObjectToken,
    DISPID_SGRSTransitions, dispid, DISPID_SRGCmdLoadFromMemory,
    DISPID_SBSSeek, SPFM_CREATE, SECHighConfidence,
    ISpeechAudioBufferInfo, SVPNormal, SPEI_ACTIVE_CATEGORY_CHANGED,
    ISpProperties, DISPID_SPPNumberOfElements,
    SpeechTokenKeyAttributes, DISPID_SWFEBlockAlign,
    DISPID_SRRPhraseInfo, SP_VISEME_0, SPEI_MAX_SR,
    DISPID_SABufferInfo, DISPID_SASetState, SDTReplacement,
    DISPID_SVEBookmark, _FILETIME, DISPID_SRSetPropertyNumber,
    DISPID_SOTCId, SGDisplay, ISpPhrase, DISPID_SRCEFalseRecognition,
    DISPID_SRGState, SAFT16kHz8BitStereo, eLEXTYPE_PRIVATE18,
    ISpeechRecoResult2, ISpeechGrammarRuleStateTransition,
    DISPID_SRSetPropertyString, SP_VISEME_14, ISpRecoCategory,
    eLEXTYPE_PRIVATE16, SGRSTTEpsilon, SPPS_RESERVED2,
    SAFT16kHz8BitMono, DISPID_SRCERecognizerStateChange, SPPS_Noun,
    ISpNotifySource, SPTEXTSELECTIONINFO, SAFT8kHz16BitStereo,
    ISpNotifySink, DISPID_SRGetFormat, SAFTTrueSpeech_8kHz1BitMono,
    DISPID_SMSSetData, DISPID_SPPFirstElement,
    DISPID_SRGSetTextSelection, DISPID_SVSkip, SP_VISEME_2,
    SPEI_MAX_TTS, SPEI_RESERVED5, DISPID_SMSALineId, SPWF_INPUT,
    DISPID_SRCEAdaptation, ISpRecoGrammar, ISpeechRecoResultTimes,
    SAFT32kHz8BitStereo, SGRSTTWildcard, DISPID_SGRName,
    DISPID_SPIGetDisplayAttributes, DISPID_SOTGetDescription,
    ISpeechPhraseRules, DISPID_SGRsCommit, SAFTCCITT_ALaw_22kHzMono,
    ISpeechXMLRecoResult, SDTDisplayText, DISPID_SRRSetTextFeedback,
    DISPID_SPRuleId, SpCustomStream, eLEXTYPE_RESERVED7, SVEAllEvents,
    DISPID_SADefaultFormat, DISPID_SRSClsidEngine, ISpResourceManager,
    SDTLexicalForm, SPEI_TTS_PRIVATE, SPEI_PROPERTY_NUM_CHANGE,
    ISpeechGrammarRuleState, ISequentialStream, DISPID_SRRSpeakAudio,
    DISPID_SASCurrentDevicePosition, DISPID_SVEventInterests,
    eLEXTYPE_PRIVATE15, DISPID_SRGetPropertyNumber,
    eLEXTYPE_RESERVED8, SRAORetainAudio, SAFT22kHz8BitStereo,
    SP_VISEME_11, ISpeechPhraseInfo, SPAR_Medium, SP_VISEME_7,
    DISPID_SRGetRecognizers, SVP_2, SRTSMLTimeout, ISpeechDataKey,
    DISPID_SPEDisplayText, ISpeechLexiconWord, SPEI_SR_BOOKMARK,
    SPEI_RESERVED2, SRERecognition, DISPID_SRSAudioStatus,
    DISPID_SGRSTsItem, DISPID_SPIEnginePrivateData, DISPID_SOTRemove,
    eLEXTYPE_VENDORLEXICON, ISpeechPhraseProperties,
    SpObjectTokenCategory, SPAUDIOBUFFERINFO, SpInprocRecognizer,
    SPEI_START_SR_STREAM, SRSActiveAlways, SSSPTRelativeToEnd,
    DISPID_SRGId, DISPID_SWFEBitsPerSample, DISPID_SDKDeleteValue,
    DISPID_SVAllowAudioOuputFormatChangesOnNextSet, DISPID_SGRsCount,
    DISPID_SRSSupportedLanguages,
    DISPID_SRAllowVoiceFormatMatchingOnNextSet, DISPID_SOTsCount,
    DISPID_SVSVisemeId, DISPID_SRCResume, SDKLCurrentUser,
    ISpStreamFormatConverter, SRSActive,
    DISPID_SRCEPropertyNumberChange, STCLocalServer,
    eLEXTYPE_PRIVATE2, DISPID_SABufferNotifySize,
    DISPID_SRRTTickCount, SPEI_UNDEFINED, DISPID_SRIsShared, SPEVENT,
    SREAdaptation, SRSEDone, DISPID_SPEAudioStreamOffset,
    SPDKL_LocalMachine, SPINTERFERENCE_TOOSLOW, SP_VISEME_20,
    SAFTCCITT_ALaw_8kHzStereo, SpeechVoiceSkipTypeSentence,
    SpeechPropertyComplexResponseSpeed, SGLexicalNoSpecialChars,
    SAFTText, DISPID_SLRemovePronunciationByPhoneIds, SVSFPersistXML,
    DISPID_SPEAudioSizeTime, SPBO_PAUSE, SPINTERFERENCE_NOISE,
    SPAUDIOSTATUS, eLEXTYPE_PRIVATE6,
    DISPID_SPANumberOfElementsInResult, SVEVoiceChange,
    DISPID_SGRSAddSpecialTransition, SVSFParseSapi,
    SPWT_LEXICAL_NO_SPECIAL_CHARS, tagSTATSTG, eLEXTYPE_RESERVED6,
    SpPhoneConverter, SPPHRASEREPLACEMENT, ISpVoice,
    SPRST_INACTIVE_WITH_PURGE, DISPID_SLPSymbolic, SPRECORESULTTIMES,
    SPSInterjection, SSTTWildcard, SGDSActiveWithAutoPause,
    DISPID_SPRulesItem, SPPHRASE, SGPronounciation, SPSMF_UPS,
    DISPID_SRRDiscardResultInfo, ISpeechVoice, DISPID_SVEAudioLevel,
    SPEI_SR_AUDIO_LEVEL, SPEI_PHRASE_START, SPPS_NotOverriden,
    SAFT44kHz8BitMono, SREBookmark, ISpeechRecognizer, DISPID_SPRText,
    SAFTCCITT_ALaw_22kHzStereo, typelib_path,
    DISPID_SRGSetWordSequenceData,
    SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN, DISPID_SRCEAudioLevel,
    SSTTTextBuffer, SpSharedRecognizer, SAFT24kHz8BitStereo,
    SpeechCategoryRecoProfiles, ISpeechTextSelectionInformation,
    SPSHT_OTHER, DISPID_SPELexicalForm, SPCS_ENABLED,
    eLEXTYPE_PRIVATE17, DISPID_SRCERecognitionForOtherContext,
    SPBINARYGRAMMAR, ISpeechAudio, SRSEIsSpeaking, SVSFNLPSpeakPunc,
    DISPID_SVVoice, DISPID_SASFreeBufferSpace, ISpeechVoiceStatus,
    ISpeechObjectToken, DISPID_SRGDictationLoad, SpAudioFormat,
    SAFT48kHz16BitStereo, SPPS_RESERVED1, DISPID_SDKGetlongValue,
    SECFNoSpecialChars, DISPID_SRRTLength, DISPID_SPAsCount,
    ISpGrammarBuilder, SAFT12kHz16BitMono, eLEXTYPE_PRIVATE8,
    SPLO_DYNAMIC, SpeechAudioFormatGUIDText, DISPID_SRCERecognition,
    SSSPTRelativeToCurrentPosition, DISPID_SVIsUISupported,
    SPEI_RESERVED6, SPCT_COMMAND, DISPID_SVSRunningState,
    DISPID_SOTs_NewEnum, DISPID_SRCEEnginePrivate,
    DISPID_SRCreateRecoContext, DISPIDSPTSI_SelectionLength,
    SPSUnknown, SPWT_DISPLAY, DISPID_SVGetAudioInputs,
    DISPID_SPRuleConfidence, SECLowConfidence, SpeechRegistryUserRoot,
    SSTTDictation, eLEXTYPE_PRIVATE19, SAFT8kHz8BitMono, BSTR,
    SFTSREngine, DISPID_SGRsFindRule, DISPID_SGRSTWeight,
    SAFTCCITT_uLaw_22kHzStereo, DISPID_SAFGuid, SAFTADPCM_22kHzStereo,
    ISpeechLexiconPronunciation, SREHypothesis, SGSExclusive,
    DISPID_SPEActualConfidence, IInternetSecurityMgrSite,
    DISPID_SGRSTs_NewEnum, SpeechTokenKeyUI,
    DISPID_SPRDisplayAttributes, SPEI_ADAPTATION,
    SpeechCategoryPhoneConverters, SPEI_SOUND_END,
    SpStreamFormatConverter, SP_VISEME_1, eLEXTYPE_PRIVATE10,
    ISpeechRecoContext, DISPID_SGRSTPropertyId,
    SpeechPropertyAdaptationOn, DISPID_SRSCurrentStreamNumber,
    SPAS_STOP, DISPID_SRSNumberOfActiveRules, SITooQuiet,
    SPAR_Unknown, DISPID_SRCVoicePurgeEvent, DISPID_SPPConfidence,
    SPCT_SUB_COMMAND, SpeechAllElements, SGSDisabled, wireHWND,
    SAFT32kHz16BitMono, SVSFlagsAsync,
    SpeechPropertyNormalConfidenceThreshold, SWTDeleted,
    SPDKL_CurrentUser, SAFT11kHz8BitMono, ISpRecoResult,
    Speech_Max_Word_Length, DISPID_SGRSTText,
    ISpeechRecoResultDispatch, STCRemoteServer,
    DISPID_SRIsUISupported, SDA_Two_Trailing_Spaces,
    SPSERIALIZEDRESULT, SPEI_RECO_STATE_CHANGE,
    DISPID_SVAudioOutputStream, DISPID_SPRsCount,
    DISPID_SRCESoundStart, SRARoot, eLEXTYPE_RESERVED4,
    SPEI_RESERVED3, DISPID_SPCIdToPhone,
    DISPID_SASCurrentSeekPosition, WAVEFORMATEX, SPAS_RUN,
    SPEI_RESERVED1, SAFT24kHz16BitStereo, DISPID_SVDisplayUI,
    ISpRecoContext2, SPSVerb, DISPID_SRStatus, SPRECOCONTEXTSTATUS,
    ISpAudio, DISPID_SOTGetAttribute, DISPID_SOTDisplayUI,
    SP_VISEME_5, SpeechGrammarTagUnlimitedDictation, SpMMAudioIn,
    DISPID_SRGCmdLoadFromProprietaryGrammar, Speech_Max_Pron_Length,
    SAFTDefault, SPGS_DISABLED, SWPUnknownWordPronounceable,
    SAFTGSM610_8kHzMono, DISPID_SPIRule, SDTProperty, SPPHRASEELEMENT,
    SREAudioLevel, DISPID_SRRSaveToMemory, ISpeechAudioStatus,
    SINoSignal, DISPID_SRRAudioFormat, WSTRING,
    DISPIDSPTSI_ActiveOffset, SAFTNoAssignedFormat,
    DISPID_SGRSTNextState, SPEI_END_INPUT_STREAM, SPEI_TTS_BOOKMARK,
    SVP_19, SAFT8kHz16BitMono, ISpPhraseAlt, DISPID_SRRAlternates,
    SAFTGSM610_22kHzMono, SWPKnownWordPronounceable, eWORDTYPE_ADDED,
    ISpDataKey, DISPID_SOTCEnumerateTokens, SVP_18,
    SPXRO_Alternates_SML, DISPID_SOTIsUISupported, SPAO_NONE,
    DISPID_SVEStreamStart, DISPID_SRGRules, SPINTERFERENCE_NONE,
    SRAExport, eLEXTYPE_PRIVATE11, SPPS_Unknown,
    SPSMF_SRGS_SAPIPROPERTIES, DISPID_SRCRetainedAudioFormat,
    DISPID_SVEStreamEnd, SAFT12kHz8BitMono, DISPID_SCSBaseStream,
    SP_VISEME_3, ISpObjectWithToken, SDA_Consume_Leading_Spaces,
    UINT_PTR, DISPID_SFSOpen, DISPID_SLPs_NewEnum,
    DISPID_SDKCreateKey, ISpeechMMSysAudio, SFTInput, SP_VISEME_10,
    SPWT_LEXICAL, eLEXTYPE_RESERVED9, _LARGE_INTEGER,
    ISpeechLexiconPronunciations,
    __MIDL___MIDL_itf_sapi_0000_0020_0001, SDKLLocalMachine,
    ISpRecognizer3, DISPID_SASState, DISPID_SVSInputSentenceLength,
    SRATopLevel, SGDSActive, DISPID_SLPType, DISPID_SOTCDefault,
    ISpeechGrammarRuleStateTransitions, DISPID_SVVolume, SpLexicon,
    VARIANT_BOOL, SDTAll, DISPID_SRRTimes, DISPID_SVEViseme,
    SpNullPhoneConverter, DISPID_SRCEPropertyStringChange,
    SpInProcRecoContext, DISPID_SLGetPronunciations,
    ISpNotifyTranslator, DISPID_SRRTStreamTime, DISPID_SPIEngineId,
    SPRST_INACTIVE, SLODynamic, SpStream, DISPID_SRCEInterference,
    SAFTADPCM_11kHzMono, SREStateChange, DISPID_SVSpeak, SPCT_SLEEP,
    SDTPronunciation, SSFMOpenForRead, SPEI_RECO_OTHER_CONTEXT,
    DISPID_SMSAMMHandle, SAFT16kHz16BitStereo, SVSFUnusedFlags,
    DISPID_SRGCmdLoadFromResource, SAFTCCITT_uLaw_11kHzStereo,
    SpeechGrammarTagDictation, DISPID_SRRAudio, SPFM_NUM_MODES,
    eLEXTYPE_PRIVATE14, STSF_CommonAppData, LONG_PTR,
    DISPID_SLRemovePronunciation, DISPID_SLPLangId,
    SpPhraseInfoBuilder, DISPID_SVWaitUntilDone, DISPID_SMSADeviceId,
    SAFTADPCM_44kHzMono, SPPHRASERULE, SP_VISEME_18,
    SpeechVoiceCategoryTTSRate, DISPID_SGRClear, tagSPPROPERTYINFO,
    eLEXTYPE_PRIVATE7, DISPID_SRCPause, DISPID_SREmulateRecognition,
    DISPID_SRCCreateResultFromMemory, eLEXTYPE_USER, SVP_14, SVP_8,
    GUID, SAFTGSM610_44kHzMono, DISPID_SOTDataKey, STCInprocServer,
    SpShortcut, SREAllEvents, DISPID_SLAddPronunciation,
    DISPID_SGRSTType, DISPID_SOTCategory, SVP_1,
    _ISpeechRecoContextEvents, SPFM_OPEN_READWRITE,
    DISPIDSPTSI_ActiveLength, ISpeechGrammarRules,
    DISPID_SAFSetWaveFormatEx, SDA_One_Trailing_Space,
    DISPID_SDKEnumKeys, DISPID_SPIGrammarId, DISPID_SPIGetText,
    DISPID_SPERetainedSizeBytes, SVEAudioLevel,
    DISPID_SRCCmdMaxAlternates, SPINTERFERENCE_LATENCY_TRUNCATE_END,
    DISPID_SVSInputWordLength, DISPID_SRGCmdLoadFromFile,
    DISPID_SVSpeakCompleteEvent, SpeechCategoryAudioOut,
    SAFTNonStandardFormat, DISPID_SPEs_NewEnum, DISPID_SLWLangId,
    ISpMMSysAudio, DISPID_SVSInputSentencePosition, SPAR_Low,
    eLEXTYPE_PRIVATE3, ISpeechPhraseProperty,
    DISPID_SRGDictationSetState, SPWORDPRONUNCIATION,
    ISpeechPhraseAlternate, IUnknown, __MIDL_IWinTypes_0009,
    DISPID_SPRuleParent, DISPID_SVSLastStreamNumberQueued,
    SAFT44kHz16BitMono, DISPID_SPEDisplayAttributes, SPRS_INACTIVE,
    DISPID_SRGIsPronounceable, SpeechTokenKeyFiles,
    DISPID_SRGDictationUnload, DISPID_SPRNumberOfElements,
    DISPID_SOTGetStorageFileName, eLEXTYPE_USER_SHORTCUT,
    DISPID_SRRRecoContext, DISPID_SOTSetId, DISPID_SVSLastResult,
    DISPID_SRGReset, DISPID_SPAs_NewEnum, SECFDefault, SPWF_SRENGINE,
    DISPID_SRCERequestUI, DISPID_SPPValue, SITooFast,
    SAFT11kHz8BitStereo, DISPID_SLGenerationId, DISPID_SGRAddResource,
    SAFTCCITT_uLaw_44kHzStereo, DISPID_SVPause, SVSFIsNotXML,
    SRSInactive, SPPS_SuppressWord, DISPID_SVEEnginePrivate,
    SpeechPropertyHighConfidenceThreshold, SINoise,
    SpeechAudioFormatGUIDWave, DISPID_SRDisplayUI,
    SAFT44kHz8BitStereo, DISPID_SPRsItem,
    DISPID_SRSCurrentStreamPosition, DISPID_SRCState,
    SpeechMicTraining, SAFTCCITT_uLaw_22kHzMono, SPRULE,
    SPAO_RETAIN_AUDIO, ISpeechPhraseElement, SRTExtendableParse,
    SAFTCCITT_uLaw_8kHzMono, DISPID_SVSLastBookmarkId,
    IEnumSpObjectTokens, SAFT44kHz16BitStereo, SPPS_LMA, SINone,
    DISPID_SDKEnumValues, _ULARGE_INTEGER, DISPID_SLWs_NewEnum,
    SAFTADPCM_44kHzStereo, DISPID_SPPBRestorePhraseFromMemory,
    SGLexical, SPVOICESTATUS, SpeechUserTraining, eLEXTYPE_MORPHOLOGY,
    SPSNotOverriden, DISPID_SRCAudioInInterferenceStatus,
    DISPID_SRCSetAdaptationData, DISPID_SPRuleName, SVP_13,
    SVSFDefault, SAFTCCITT_uLaw_11kHzMono, SPPHRASEPROPERTY,
    SPPS_Function, SVP_12, DISPID_SLWType, ISpeechWaveFormatEx,
    eWORDTYPE_DELETED, SPEI_REQUEST_UI, SPCT_DICTATION,
    SAFT48kHz16BitMono, DISPID_SPEPronunciation, SAFT11kHz16BitMono,
    SAFTCCITT_ALaw_8kHzMono, SPSHT_Unknown, COMMETHOD, SRAImport,
    SPSNoun, SVESentenceBoundary, DISPID_SABIBufferSize,
    DISPID_SPCPhoneToId, DISPID_SLGetGenerationChange, SRCS_Disabled,
    SpUnCompressedLexicon, SPPS_Modifier, SpeechCategoryRecognizers,
    DISPID_SPERequiredConfidence, _RemotableHandle,
    DISPID_SPRuleFirstElement, Speech_StreamPos_RealTime,
    SRERecoOtherContext, SPWP_KNOWN_WORD_PRONOUNCEABLE,
    SSFMOpenReadWrite, SPRS_ACTIVE_USER_DELIMITED, SDTAlternates,
    DISPID_SPRuleEngineConfidence, DISPID_SPACommit, SPSFunction,
    SPPS_Noncontent, DISPID_SGRSAddWordTransition,
    SAFT48kHz8BitStereo, DISPID_SLPPhoneIds, DISPID_SDKDeleteKey,
    DISPID_SGRAddState, SPEI_RECOGNITION, DISPID_SRProfile, SPSLMA,
    SpeechPropertyResourceUsage, SPSEMANTICERRORINFO,
    DISPID_SRAllowAudioInputFormatChangesOnNextSet, SPLO_STATIC,
    DISPID_SRCESoundEnd, SDTRule, SVEViseme, IStream, SSFMCreate,
    ISpeechLexicon, SP_VISEME_19, eLEXTYPE_PRIVATE12,
    DISPID_SPEsCount, SGRSTTRule, SVP_6, SPSERIALIZEDPHRASE,
    DISPID_SABIEventBias, SpeechEngineProperties,
    DISPID_SVSpeakStream, DISPID_SPRulesCount, ISpeechLexiconWords,
    DISPID_SRCRetainedAudio, ISpPhoneConverter, SPEI_VOICE_CHANGE,
    DISPID_SASNonBlockingIO, SPPS_RESERVED3, DISPID_SVEVoiceChange,
    SPSHORTCUTPAIR, SpMMAudioEnum, SPAR_High, SVP_21,
    SpeechPropertyResponseSpeed, SPAS_CLOSED, SPAS_PAUSE,
    eLEXTYPE_PRIVATE20, DISPID_SPEsItem, SPINTERFERENCE_TOOLOUD,
    DISPID_SDKGetStringValue, DISPID_SLAddPronunciationByPhoneIds,
    DISPID_SPRuleChildren, SVSFParseAutodetect, DISPID_SPRs_NewEnum,
    SVP_16, SREPropertyNumChange, SLOStatic, SPEI_TTS_AUDIO_LEVEL,
    DISPID_SLWPronunciations, ISpPhoneticAlphabetConverter,
    SRTEmulated, SASPause, ISpRecoGrammar2, SpeechAudioVolume,
    DISPID_SRCCreateGrammar, DISPID_SPAPhraseInfo, SECFIgnoreKanaType,
    DISPID_SLPsCount, SSFMCreateForWrite, SPCS_DISABLED,
    DISPID_SWFEChannels, SpTextSelectionInformation,
    DISPID_SWFESamplesPerSec, DISPID_SDKSetStringValue, SVP_17,
    SPEI_MIN_TTS, SAFT32kHz16BitStereo, SVF_None,
    DISPID_SPEAudioTimeOffset, SPGS_EXCLUSIVE, SP_VISEME_21,
    SITooLoud, eLEXTYPE_LETTERTOSOUND, SVF_Stressed,
    ISpeechGrammarRule, DISPID_SGRsDynamic, SVSFIsFilename, SVPOver,
    DISPID_SVAlertBoundary, SPVPRI_NORMAL, ISpSerializeState,
    DISPID_SGRInitialState, SREPhraseStart, SpResourceManager,
    VARIANT, SPSMF_SRGS_SEMANTICINTERPRETATION_W3C,
    DISPID_SPIAudioSizeTime, DISPID_SPILanguageId,
    SpeechAddRemoveWord, DISPID_SWFEAvgBytesPerSec, SRTAutopause,
    ISpLexicon, SP_VISEME_15, SAFTCCITT_ALaw_11kHzStereo,
    DISPID_SGRSAddRuleTransition, SAFTCCITT_ALaw_11kHzMono, ULONG_PTR,
    DISPID_SPAStartElementInResult, SRESoundEnd, DISPID_SAEventHandle,
    SITooSlow, SPSHT_EMAIL, SPFM_OPEN_READONLY,
    SPWP_UNKNOWN_WORD_PRONOUNCEABLE, DISPID_SRGetPropertyString,
    SAFTCCITT_uLaw_8kHzStereo, DISPID_SLWsItem, SPEI_END_SR_STREAM,
    SPRST_ACTIVE, SAFT22kHz16BitMono, SAFT11kHz16BitStereo,
    DISPID_SPARecoResult
)


class SPWAVEFORMATTYPE(IntFlag):
    SPWF_INPUT = 0
    SPWF_SRENGINE = 1


class SPDATAKEYLOCATION(IntFlag):
    SPDKL_DefaultLocation = 0
    SPDKL_CurrentUser = 1
    SPDKL_LocalMachine = 2
    SPDKL_CurrentConfig = 5


class SpeechDisplayAttributes(IntFlag):
    SDA_No_Trailing_Space = 0
    SDA_One_Trailing_Space = 2
    SDA_Two_Trailing_Spaces = 4
    SDA_Consume_Leading_Spaces = 8


class SpeechEngineConfidence(IntFlag):
    SECLowConfidence = -1
    SECNormalConfidence = 0
    SECHighConfidence = 1


class SpeechStreamSeekPositionType(IntFlag):
    SSSPTRelativeToStart = 0
    SSSPTRelativeToCurrentPosition = 1
    SSSPTRelativeToEnd = 2


class SpeechAudioState(IntFlag):
    SASClosed = 0
    SASStop = 1
    SASPause = 2
    SASRun = 3


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


class SpeechRecognizerState(IntFlag):
    SRSInactive = 0
    SRSActive = 1
    SRSActiveAlways = 2
    SRSInactiveWithPurge = 3


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


class SpeechWordType(IntFlag):
    SWTAdded = 1
    SWTDeleted = 2


class _SPAUDIOSTATE(IntFlag):
    SPAS_CLOSED = 0
    SPAS_STOP = 1
    SPAS_PAUSE = 2
    SPAS_RUN = 3


class SpeechRuleState(IntFlag):
    SGDSInactive = 0
    SGDSActive = 1
    SGDSActiveWithAutoPause = 3
    SGDSActiveUserDelimited = 4


class SpeechWordPronounceable(IntFlag):
    SWPUnknownWordUnpronounceable = 0
    SWPUnknownWordPronounceable = 1
    SWPKnownWordPronounceable = 2


class SpeechSpecialTransitionType(IntFlag):
    SSTTWildcard = 1
    SSTTDictation = 2
    SSTTTextBuffer = 3


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


class SPXMLRESULTOPTIONS(IntFlag):
    SPXRO_SML = 0
    SPXRO_Alternates_SML = 1


class SPFILEMODE(IntFlag):
    SPFM_OPEN_READONLY = 0
    SPFM_OPEN_READWRITE = 1
    SPFM_CREATE = 2
    SPFM_CREATE_ALWAYS = 3
    SPFM_NUM_MODES = 4


class SpeechTokenContext(IntFlag):
    STCInprocServer = 1
    STCInprocHandler = 2
    STCLocalServer = 4
    STCRemoteServer = 16
    STCAll = 23


class SpeechTokenShellFolder(IntFlag):
    STSF_AppData = 26
    STSF_LocalAppData = 28
    STSF_CommonAppData = 35
    STSF_FlagCreate = 32768


class SpeechDataKeyLocation(IntFlag):
    SDKLDefaultLocation = 0
    SDKLCurrentUser = 1
    SDKLLocalMachine = 2
    SDKLCurrentConfig = 5


class SpeechBookmarkOptions(IntFlag):
    SBONone = 0
    SBOPause = 1


class SpeechFormatType(IntFlag):
    SFTInput = 0
    SFTSREngine = 1


class SpeechRecognitionType(IntFlag):
    SRTStandard = 0
    SRTAutopause = 1
    SRTEmulated = 2
    SRTSMLTimeout = 4
    SRTExtendableParse = 8
    SRTReSent = 16


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


class SPRECOSTATE(IntFlag):
    SPRST_INACTIVE = 0
    SPRST_ACTIVE = 1
    SPRST_ACTIVE_ALWAYS = 2
    SPRST_INACTIVE_WITH_PURGE = 3
    SPRST_NUM_STATES = 4


class SpeechInterference(IntFlag):
    SINone = 0
    SINoise = 1
    SINoSignal = 2
    SITooLoud = 3
    SITooQuiet = 4
    SITooFast = 5
    SITooSlow = 6


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


class DISPID_SpeechObjectTokens(IntFlag):
    DISPID_SOTsCount = 1
    DISPID_SOTsItem = 0
    DISPID_SOTs_NewEnum = -4


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


class DISPID_SpeechBaseStream(IntFlag):
    DISPID_SBSFormat = 1
    DISPID_SBSRead = 2
    DISPID_SBSWrite = 3
    DISPID_SBSSeek = 4


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


class DISPID_SpeechFileStream(IntFlag):
    DISPID_SFSOpen = 100
    DISPID_SFSClose = 101


class DISPID_SpeechCustomStream(IntFlag):
    DISPID_SCSBaseStream = 100


class DISPID_SpeechMemoryStream(IntFlag):
    DISPID_SMSSetData = 100
    DISPID_SMSGetData = 101


class DISPID_SpeechAudioStatus(IntFlag):
    DISPID_SASFreeBufferSpace = 1
    DISPID_SASNonBlockingIO = 2
    DISPID_SASState = 3
    DISPID_SASCurrentSeekPosition = 4
    DISPID_SASCurrentDevicePosition = 5


class DISPID_SpeechAudioBufferInfo(IntFlag):
    DISPID_SABIMinNotification = 1
    DISPID_SABIBufferSize = 2
    DISPID_SABIEventBias = 3


class DISPID_SpeechWaveFormatEx(IntFlag):
    DISPID_SWFEFormatTag = 1
    DISPID_SWFEChannels = 2
    DISPID_SWFESamplesPerSec = 3
    DISPID_SWFEAvgBytesPerSec = 4
    DISPID_SWFEBlockAlign = 5
    DISPID_SWFEBitsPerSample = 6
    DISPID_SWFEExtraData = 7


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


class SpeechEmulationCompareFlags(IntFlag):
    SECFIgnoreCase = 1
    SECFIgnoreKanaType = 65536
    SECFIgnoreWidth = 131072
    SECFNoSpecialChars = 536870912
    SECFEmulateResult = 1073741824
    SECFDefault = 196609


class DISPID_SpeechRecognizerStatus(IntFlag):
    DISPID_SRSAudioStatus = 1
    DISPID_SRSCurrentStreamPosition = 2
    DISPID_SRSCurrentStreamNumber = 3
    DISPID_SRSNumberOfActiveRules = 4
    DISPID_SRSClsidEngine = 5
    DISPID_SRSSupportedLanguages = 6


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


class SpeechGrammarState(IntFlag):
    SGSEnabled = 1
    SGSDisabled = 0
    SGSExclusive = 3


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


class DISPID_SpeechGrammarRule(IntFlag):
    DISPID_SGRAttributes = 1
    DISPID_SGRInitialState = 2
    DISPID_SGRName = 3
    DISPID_SGRId = 4
    DISPID_SGRClear = 5
    DISPID_SGRAddResource = 6
    DISPID_SGRAddState = 7


class DISPID_SpeechGrammarRules(IntFlag):
    DISPID_SGRsCount = 1
    DISPID_SGRsDynamic = 2
    DISPID_SGRsAdd = 3
    DISPID_SGRsCommit = 4
    DISPID_SGRsCommitAndSave = 5
    DISPID_SGRsFindRule = 6
    DISPID_SGRsItem = 0
    DISPID_SGRs_NewEnum = -4


class DISPID_SpeechGrammarRuleState(IntFlag):
    DISPID_SGRSRule = 1
    DISPID_SGRSTransitions = 2
    DISPID_SGRSAddWordTransition = 3
    DISPID_SGRSAddRuleTransition = 4
    DISPID_SGRSAddSpecialTransition = 5


class SpeechVisemeFeature(IntFlag):
    SVF_None = 0
    SVF_Stressed = 1
    SVF_Emphasis = 2


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


class DISPIDSPTSI(IntFlag):
    DISPIDSPTSI_ActiveOffset = 1
    DISPIDSPTSI_ActiveLength = 2
    DISPIDSPTSI_SelectionOffset = 3
    DISPIDSPTSI_SelectionLength = 4


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


class DISPID_SpeechXMLRecoResult(IntFlag):
    DISPID_SRRGetXMLResult = 10
    DISPID_SRRGetXMLErrorInfo = 11


class DISPID_SpeechRecoResult2(IntFlag):
    DISPID_SRRSetTextFeedback = 12


class DISPID_SpeechPhraseBuilder(IntFlag):
    DISPID_SPPBRestorePhraseFromMemory = 1


class SpeechRunState(IntFlag):
    SRSEDone = 1
    SRSEIsSpeaking = 2


class DISPID_SpeechRecoResultTimes(IntFlag):
    DISPID_SRRTStreamTime = 1
    DISPID_SRRTLength = 2
    DISPID_SRRTTickCount = 3
    DISPID_SRRTOffsetFromStart = 4


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


class SpeechRuleAttributes(IntFlag):
    SRATopLevel = 1
    SRADefaultToActive = 2
    SRAExport = 4
    SRAImport = 8
    SRAInterpreter = 16
    SRADynamic = 32
    SRARoot = 64


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


class SpeechGrammarWordType(IntFlag):
    SGDisplay = 0
    SGLexical = 1
    SGPronounciation = 2
    SGLexicalNoSpecialChars = 3


class SPAUDIOOPTIONS(IntFlag):
    SPAO_NONE = 0
    SPAO_RETAIN_AUDIO = 1


class SPBOOKMARKOPTIONS(IntFlag):
    SPBO_NONE = 0
    SPBO_PAUSE = 1
    SPBO_AHEAD = 2
    SPBO_TIME_UNITS = 4


class SPCONTEXTSTATE(IntFlag):
    SPCS_DISABLED = 0
    SPCS_ENABLED = 1


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


class DISPID_SpeechPhraseRules(IntFlag):
    DISPID_SPRulesCount = 1
    DISPID_SPRulesItem = 0
    DISPID_SPRules_NewEnum = -4


class SpeechGrammarRuleStateTransitionType(IntFlag):
    SGRSTTEpsilon = 0
    SGRSTTWord = 1
    SGRSTTRule = 2
    SGRSTTDictation = 3
    SGRSTTWildcard = 4
    SGRSTTTextBuffer = 5


class DISPID_SpeechLexicon(IntFlag):
    DISPID_SLGenerationId = 1
    DISPID_SLGetWords = 2
    DISPID_SLAddPronunciation = 3
    DISPID_SLAddPronunciationByPhoneIds = 4
    DISPID_SLRemovePronunciation = 5
    DISPID_SLRemovePronunciationByPhoneIds = 6
    DISPID_SLGetPronunciations = 7
    DISPID_SLGetGenerationChange = 8


class DISPID_SpeechLexiconWords(IntFlag):
    DISPID_SLWsCount = 1
    DISPID_SLWsItem = 0
    DISPID_SLWs_NewEnum = -4


class DISPID_SpeechLexiconWord(IntFlag):
    DISPID_SLWLangId = 1
    DISPID_SLWType = 2
    DISPID_SLWWord = 3
    DISPID_SLWPronunciations = 4


class DISPID_SpeechLexiconProns(IntFlag):
    DISPID_SLPsCount = 1
    DISPID_SLPsItem = 0
    DISPID_SLPs_NewEnum = -4


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


class SPSEMANTICFORMAT(IntFlag):
    SPSMF_SAPI_PROPERTIES = 0
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS = 1
    SPSMF_SRGS_SAPIPROPERTIES = 2
    SPSMF_UPS = 4
    SPSMF_SRGS_SEMANTICINTERPRETATION_W3C = 8


class SPGRAMMARWORDTYPE(IntFlag):
    SPWT_DISPLAY = 0
    SPWT_LEXICAL = 1
    SPWT_PRONUNCIATION = 2
    SPWT_LEXICAL_NO_SPECIAL_CHARS = 3


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


class SpeechVoicePriority(IntFlag):
    SVPNormal = 0
    SVPAlert = 1
    SVPOver = 2


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


class SpeechStreamFileMode(IntFlag):
    SSFMOpenForRead = 0
    SSFMOpenReadWrite = 1
    SSFMCreate = 2
    SSFMCreateForWrite = 3


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


class SPADAPTATIONRELEVANCE(IntFlag):
    SPAR_Unknown = 0
    SPAR_Low = 1
    SPAR_Medium = 2
    SPAR_High = 3


class SPCATEGORYTYPE(IntFlag):
    SPCT_COMMAND = 0
    SPCT_DICTATION = 1
    SPCT_SLEEP = 2
    SPCT_SUB_COMMAND = 3
    SPCT_SUB_DICTATION = 4


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


class SPWORDTYPE(IntFlag):
    eWORDTYPE_ADDED = 1
    eWORDTYPE_DELETED = 2


class SPSHORTCUTTYPE(IntFlag):
    SPSHT_NotOverriden = -1
    SPSHT_Unknown = 0
    SPSHT_EMAIL = 4096
    SPSHT_OTHER = 8192
    SPPS_RESERVED1 = 12288
    SPPS_RESERVED2 = 16384
    SPPS_RESERVED3 = 20480
    SPPS_RESERVED4 = 61440


class SpeechLoadOption(IntFlag):
    SLOStatic = 0
    SLODynamic = 1


SPSTREAMFORMATTYPE = SPWAVEFORMATTYPE
SPAUDIOSTATE = _SPAUDIOSTATE


__all__ = [
    'eLEXTYPE_PRIVATE17', 'DISPID_SRCERecognitionForOtherContext',
    'DISPID_SRCEHypothesis', 'SPBINARYGRAMMAR', 'SPBO_AHEAD',
    'DISPID_SVGetProfiles', 'ISpeechAudio', 'ISpeechRecoResult',
    'SVSFNLPSpeakPunc', 'DISPID_SVVoice', 'DISPID_SASFreeBufferSpace',
    'SRSEIsSpeaking', 'SPINTERFERENCE_LATENCY_WARNING', 'SP_VISEME_8',
    'eLEXTYPE_RESERVED10', 'DISPID_SpeechAudioStatus',
    'ISpeechVoiceStatus', 'SPEI_PHONEME', 'SVEWordBoundary',
    'ISpeechObjectToken', 'DISPID_SRGDictationLoad', 'SPAUDIOSTATE',
    'SBONone', 'DISPID_SRAudioInputStream', 'SpAudioFormat',
    'DISPID_SPIStartTime', 'DISPID_SPERetainedStreamOffset',
    'SPFM_CREATE_ALWAYS', 'SVSFParseMask', 'SAFT48kHz16BitStereo',
    'SPCATEGORYTYPE', 'SpNotifyTranslator', 'SPPS_RESERVED1',
    'IInternetSecurityManager', 'DISPID_SDKGetlongValue',
    'DISPID_SpeechPhraseInfo', 'SECFNoSpecialChars',
    'DISPID_SDKOpenKey', 'Library', 'DISPID_SRRTLength',
    'ISpeechAudioFormat', 'ISpRecoContext', 'DISPID_SDKSetLongValue',
    'eLEXTYPE_PRIVATE13', 'DISPID_SRRTOffsetFromStart',
    'ISpObjectTokenCategory', 'DISPID_SPAsCount', 'ISpGrammarBuilder',
    'SPBOOKMARKOPTIONS', 'SAFT12kHz16BitMono', 'eLEXTYPE_PRIVATE8',
    'eLEXTYPE_PRIVATE5', 'ISpeechPhraseAlternates', 'SPLO_DYNAMIC',
    'SpeechAudioFormatGUIDText', 'DISPID_SRCERecognition',
    'SSSPTRelativeToCurrentPosition', 'SPVPRI_OVER',
    'DISPID_SVIsUISupported', 'DISPID_SGRSRule', 'DISPID_SPCLangId',
    'SPEI_RESERVED6', 'DISPID_SpeechPhraseAlternates', 'SPCT_COMMAND',
    'DISPID_SpeechRecoResultTimes', 'SPVPRI_ALERT',
    'DISPID_SVSRunningState', 'DISPID_SOTs_NewEnum',
    'SVEEndInputStream', 'IEnumString', 'SPEVENTSOURCEINFO', 'SVP_5',
    'DISPID_SRCEEnginePrivate', 'SWPUnknownWordUnpronounceable',
    'DISPID_SRCreateRecoContext', 'DISPIDSPTSI_SelectionLength',
    'SPSUnknown', 'DISPID_SLGetWords', 'SPWT_DISPLAY',
    'DISPID_SpeechRecognizer', 'DISPID_SVGetAudioInputs', 'SVP_0',
    'DISPID_SRState', 'DISPID_SPRuleConfidence', 'SVSFIsXML',
    'SpeechTokenValueCLSID', 'SECLowConfidence', 'SVP_11',
    'ISpPhoneticAlphabetSelection', 'SGRSTTWord', 'SVP_3',
    'ISpeechPhraseRule', 'STSF_FlagCreate', 'DISPID_SVRate',
    'SpeechWordType', 'DISPID_SOTCreateInstance',
    'DISPID_SRGCmdSetRuleState', 'SVP_10', 'SPSModifier',
    'SSTTDictation', 'SpeechRegistryUserRoot', 'SPLEXICONTYPE',
    'eLEXTYPE_PRIVATE19', 'SAFT8kHz8BitMono', 'DISPID_SOTCSetId',
    'SpeechDisplayAttributes', 'STSF_AppData', 'SFTSREngine',
    'DISPID_SBSWrite', 'SpeechRecoEvents', 'DISPID_SGRsFindRule',
    'DISPID_SGRSTWeight', 'SPWAVEFORMATTYPE',
    'DISPID_SPIRetainedSizeBytes', 'SPBO_NONE', 'DISPID_SAFGuid',
    'SpCompressedLexicon', 'SAFTADPCM_22kHzStereo',
    '__MIDL___MIDL_itf_sapi_0000_0020_0002',
    'ISpeechLexiconPronunciation', 'SDTAudio', 'SREHypothesis',
    'SGSExclusive', 'ISpStream', 'DISPID_SpeechPhraseBuilder',
    'SASStop', 'DISPID_SPEActualConfidence',
    'IInternetSecurityMgrSite', 'SPCT_SUB_DICTATION',
    'DISPID_SGRSTs_NewEnum', 'Speech_Default_Weight',
    'SpeechTokenKeyUI', 'DISPID_SPRDisplayAttributes',
    'SPEI_ADAPTATION', 'SRADefaultToActive', 'SpeechPartOfSpeech',
    'SpeechCategoryPhoneConverters', 'SPEI_SOUND_END',
    'SpeechRegistryLocalMachineRoot', 'DISPID_SPPEngineConfidence',
    'SRAInterpreter', 'eLEXTYPE_PRIVATE9', 'SPSSuppressWord',
    'ISpRecognizer2', 'SP_VISEME_1', 'SpStreamFormatConverter',
    'eLEXTYPE_PRIVATE10', 'SPXRO_SML', 'SPRECOSTATE',
    'ISpeechRecoContext', 'DISPID_SGRSTPropertyId',
    'eLEXTYPE_PRIVATE1', 'SpeechPropertyAdaptationOn',
    'DISPID_SpeechRecoContext', 'SRESoundStart',
    'DISPID_SRSCurrentStreamNumber', 'DISPID_SpeechPhoneConverter',
    'DISPID_SRAudioInput', 'SAFT22kHz8BitMono', 'eLEXTYPE_PRIVATE12',
    'DISPID_SOTsItem', 'SLTUser', 'SPAS_STOP',
    'DISPID_SRSNumberOfActiveRules', 'SpeechRecognizerState',
    'SVEStartInputStream', 'ISpeechObjectTokens', 'SPGRAMMARSTATE',
    'SVP_9', 'SAFTADPCM_8kHzStereo', 'SITooQuiet', 'SPAR_Unknown',
    'DISPID_SpeechLexiconProns', 'DISPID_SRCVoicePurgeEvent',
    'SSSPTRelativeToStart', 'ISpeechRecognizerStatus',
    'DISPID_SVSyncronousSpeakTimeout', 'SpeechAllElements',
    'SGSDisabled', 'DISPID_SPPConfidence', 'SpeechStreamFileMode',
    'SGDSActiveUserDelimited', 'SAFT32kHz16BitMono', 'SVSFlagsAsync',
    'Speech_StreamPos_Asap', 'DISPID_SRCEEndStream',
    'SpeechPropertyNormalConfidenceThreshold', 'STCInprocHandler',
    'SPEI_PROPERTY_STRING_CHANGE', 'SWTDeleted', 'ISpRecognizer',
    'DISPID_SpeechLexicon', 'SPDKL_CurrentUser',
    'DISPID_SPRFirstElement', 'SAFT11kHz8BitMono', 'SPPROPERTYINFO',
    'DISPID_SpeechAudioBufferInfo', 'DISPID_SPEEngineConfidence',
    'SpeechVisemeFeature', 'ISpRecoResult', 'Speech_Max_Word_Length',
    'DISPID_SAFGetWaveFormatEx', 'DISPID_SGRSTText',
    'ISpeechRecoResultDispatch', 'STCRemoteServer',
    'SPEI_INTERFERENCE', 'DISPID_SRIsUISupported',
    'SDA_Two_Trailing_Spaces', 'SPSERIALIZEDRESULT',
    'SPWORDPRONUNCIATIONLIST', 'STCAll', 'SpFileStream',
    'SPEI_RECO_STATE_CHANGE', 'DISPID_SpeechObjectTokens',
    'eLEXTYPE_PRIVATE4', 'DISPID_SFSClose',
    'DISPID_SVAudioOutputStream', 'DISPID_SPRsCount',
    'SAFT16kHz16BitMono', 'DISPID_SRCESoundStart',
    'SPEI_SR_RETAINEDAUDIO', 'SPLOADOPTIONS', 'SRERequestUI',
    'SRARoot', 'ISpeechPhraseReplacements', 'DISPID_SpeechAudio',
    'SREStreamStart', 'SRCS_Enabled', 'SPXMLRESULTOPTIONS',
    'SPEI_RESERVED3', 'eLEXTYPE_RESERVED4', 'DISPID_SPCIdToPhone',
    'DISPID_SGRs_NewEnum', 'SpeechDictationTopicSpelling',
    'DISPID_SASCurrentSeekPosition',
    'DISPID_SpeechGrammarRuleStateTransition', 'DISPID_SGRsAdd',
    'SECFIgnoreWidth', 'SPSHT_NotOverriden',
    'SAFTCCITT_uLaw_44kHzMono', 'WAVEFORMATEX',
    'DISPID_SVGetAudioOutputs', 'SPAS_RUN', 'SVP_7', 'SPEI_RESERVED1',
    'SAFT24kHz16BitStereo', 'SREPrivate', 'SpeechRecognitionType',
    'SpWaveFormatEx', 'DISPID_SVDisplayUI',
    'DISPID_SGRSTPropertyName', 'ISpRecoContext2', 'SPPS_RESERVED4',
    'SVSFPurgeBeforeSpeak', 'SPSVerb', 'DISPID_SVSPhonemeId',
    'DISPID_SRStatus', 'DISPID_SRCEBookmark', 'ISpAudio',
    'DISPID_SOTGetAttribute', 'SPRECOCONTEXTSTATUS', 'SPAUDIOOPTIONS',
    'DISPID_SOTDisplayUI', 'SPEI_FALSE_RECOGNITION', 'SWTAdded',
    'SpeechTokenIdUserLexicon', 'SP_VISEME_5',
    'SpeechGrammarTagUnlimitedDictation', 'ISpeechPhraseInfoBuilder',
    'SPSEMANTICFORMAT', 'SpMMAudioIn', 'DISPID_SRGRecoContext',
    'DISPID_SRGCmdLoadFromProprietaryGrammar', 'DISPID_SPIProperties',
    'Speech_Max_Pron_Length', 'SAFTDefault', 'ISpeechRecoGrammar',
    'SPEI_WORD_BOUNDARY', 'SWPUnknownWordPronounceable',
    'SAFTGSM610_8kHzMono', 'SPGS_DISABLED', 'DISPID_SVAudioOutput',
    'DISPID_SPIRule', 'SVEBookmark', 'SDTProperty', 'SPPHRASEELEMENT',
    'SREAudioLevel', 'DISPID_SRRSaveToMemory', 'ISpeechAudioStatus',
    'SINoSignal', 'DISPID_SRRAudioFormat', 'DISPID_SOTId',
    'SGRSTTDictation', 'DISPID_SGRSTsCount',
    'DISPID_SpeechPhraseRule', 'DISPID_SPISaveToMemory',
    'DISPIDSPTSI_ActiveOffset', 'SAFTNoAssignedFormat',
    'DISPID_SGRSTNextState', 'ISpeechFileStream',
    'SPEI_END_INPUT_STREAM', 'SPRST_NUM_STATES',
    'SPINTERFERENCE_TOOQUIET', 'SPPS_Verb', 'SPPS_Interjection',
    'DISPID_SVSLastBookmark', 'SPWORD', 'DISPID_SOTMatchesAttributes',
    'SREFalseRecognition', 'SpVoice', 'SREInterference',
    'SPEI_TTS_BOOKMARK', 'SVP_19', 'SAFT8kHz16BitMono',
    'DISPID_SRCEPhraseStart', 'ISpPhraseAlt', 'SRAONone',
    'ISpeechResourceLoader', 'DISPIDSPRG', 'DISPID_SRRAlternates',
    'SWPKnownWordPronounceable', 'SAFT22kHz16BitStereo',
    'SAFTGSM610_22kHzMono', 'SpeechStreamSeekPositionType',
    'DISPID_SOTCGetDataKey', 'SPGS_ENABLED', 'DISPID_SpeechVoice',
    'eWORDTYPE_ADDED', 'ISpDataKey', 'DISPID_SOTCEnumerateTokens',
    'DISPID_SRCEventInterests', 'SVP_18', 'SPXRO_Alternates_SML',
    'SVP_15', 'DISPID_SAStatus', 'SGSEnabled', 'SDKLDefaultLocation',
    'DISPID_SOTIsUISupported', 'STSF_LocalAppData',
    'DISPID_SRGCommit', 'SPSMF_SRGS_SEMANTICINTERPRETATION_MS',
    'SpeechAudioProperties', 'DISPID_SVEStreamStart', 'SPAO_NONE',
    'DISPID_SRGRules', 'SPINTERFERENCE_NONE', 'SRAExport',
    'eLEXTYPE_PRIVATE11', 'SECFEmulateResult', 'SpMemoryStream',
    'SPSMF_SRGS_SAPIPROPERTIES', 'SPPS_Unknown',
    'DISPID_SpeechWaveFormatEx', 'DISPID_SRCRetainedAudioFormat',
    'DISPID_SpeechPhraseProperty', 'DISPID_SVEStreamEnd',
    'ISpEventSink', 'SP_VISEME_16', 'SAFT12kHz8BitMono',
    'DISPID_SCSBaseStream', 'DISPID_SpeechGrammarRule', 'SPWORDLIST',
    'SP_VISEME_3', 'DISPID_SPIAudioSizeBytes', 'SpeechInterference',
    'ISpObjectWithToken', 'SDA_Consume_Leading_Spaces', 'UINT_PTR',
    'DISPID_SVESentenceBoundary', 'DISPID_SPPName', 'DISPID_SFSOpen',
    'DISPID_SOTRemoveStorageFileName', 'DISPID_SLPs_NewEnum',
    'DISPID_SWFEExtraData', 'DISPID_SPPsCount', 'SP_VISEME_13',
    'SAFT12kHz16BitStereo', 'DISPID_SGRSTPropertyValue',
    'DISPID_SDKCreateKey', 'ISpeechMMSysAudio', 'SPRST_ACTIVE_ALWAYS',
    'SFTInput', 'DISPID_SRRGetXMLErrorInfo', 'SP_VISEME_10',
    'ISpeechCustomStream', 'SPWT_LEXICAL',
    'DISPID_SVSCurrentStreamNumber', 'eLEXTYPE_RESERVED9',
    'ISpeechLexiconPronunciations', 'SVPAlert',
    'SAFTCCITT_ALaw_44kHzMono',
    '__MIDL___MIDL_itf_sapi_0000_0020_0001', 'SpeechGrammarState',
    'SDKLLocalMachine', 'DISPID_SGRAttributes', 'SPRECOGNIZERSTATUS',
    'ISpShortcut', 'SPEI_SOUND_START', 'ISpRecognizer3',
    'DISPID_SAVolume', 'SpeechWordPronounceable', 'DISPID_SASState',
    'SRADynamic', 'SPFILEMODE', 'DISPID_SVSInputSentenceLength',
    'SRATopLevel', 'SpeechTokenShellFolder', 'SAFTGSM610_11kHzMono',
    'DISPID_SRCBookmark', 'ISpeechPhraseReplacement', 'SGDSActive',
    'ISpStreamFormat', 'DISPID_SLPType', 'SLTApp', 'SGDSInactive',
    'DISPID_SOTCDefault', 'ISpeechGrammarRuleStateTransitions',
    'SpeechLoadOption', 'DISPID_SVVolume', 'DISPID_SLPPartOfSpeech',
    'SpLexicon', 'SECNormalConfidence', 'SAFT24kHz16BitMono',
    'SDTAll', 'DISPID_SVEWord', 'DISPID_SRRTimes', 'DISPID_SVEViseme',
    'SpeechGrammarRuleStateTransitionType',
    'DISPID_SRCEPropertyStringChange', 'SpNullPhoneConverter',
    'SpInProcRecoContext', 'SAFT32kHz8BitMono',
    'DISPID_SLGetPronunciations', 'ISpNotifyTranslator',
    'SP_VISEME_9', 'DISPID_SABIMinNotification',
    'DISPID_SRRTStreamTime', 'SVP_20', 'DISPID_SPIReplacements',
    'SPRST_INACTIVE', 'DISPID_SPIEngineId', 'SPBO_TIME_UNITS',
    'DISPID_SpeechXMLRecoResult', 'SLODynamic', 'SpStream',
    'DISPID_SpeechFileStream', 'DISPID_SPPChildren',
    'DISPID_SRCEInterference', 'SPWT_PRONUNCIATION', 'SpeechRunState',
    'SAFTADPCM_11kHzMono', 'ISpeechMemoryStream', 'SREStateChange',
    'DISPID_SVSpeak', 'SVSFVoiceMask', 'DISPID_SDKGetBinaryValue',
    'DISPID_SpeechPhraseRules', 'DISPID_SVSInputWordPosition',
    'SpeechCategoryAppLexicons', 'DISPID_SGRId', 'SPSHORTCUTPAIRLIST',
    'SASClosed', 'ISpeechObjectTokenCategory', 'SPCT_SLEEP',
    'DISPIDSPTSI_SelectionOffset', 'SDTPronunciation',
    'DISPID_SVResume', 'SSFMOpenForRead', 'DISPID_SGRSTRule',
    'SPEI_RECO_OTHER_CONTEXT', 'SPEI_VISEME', 'DISPID_SMSAMMHandle',
    'DISPID_SLWsCount', 'SAFT16kHz16BitStereo', 'SVSFUnusedFlags',
    'SRTStandard', 'DISPID_SRGCmdLoadFromResource', 'DISPID_SLPsItem',
    'SPDKL_DefaultLocation', 'SpeechGrammarTagDictation',
    'DISPID_SRRAudio', 'SAFTCCITT_uLaw_11kHzStereo',
    'SAFTADPCM_11kHzStereo', 'DISPID_SpeechCustomStream',
    'SPFM_NUM_MODES', 'SPWORDTYPE', 'eLEXTYPE_PRIVATE14',
    'SPEI_START_INPUT_STREAM', 'STSF_CommonAppData', 'LONG_PTR',
    'DISPID_SLRemovePronunciation', 'DISPID_SLPLangId',
    'SAFT24kHz8BitMono', 'SPINTERFERENCE_NOSIGNAL',
    'SpPhraseInfoBuilder', 'DISPID_SVWaitUntilDone', 'SVEPrivate',
    'SECFIgnoreCase', 'DISPID_SMSADeviceId', 'SAFTADPCM_44kHzMono',
    'SpeechCategoryAudioIn', 'SPEI_SENTENCE_BOUNDARY', 'SPPHRASERULE',
    'SP_VISEME_18', 'DISPID_SGRsItem', 'SpeechVoiceCategoryTTSRate',
    'SPINTERFERENCE_TOOFAST', 'ISpEventSource', 'DISPID_SRRecognizer',
    'DISPID_SGRsCommitAndSave', 'SGRSTTTextBuffer',
    'DISPID_SpeechDataKey', 'DISPID_SpeechPhraseElement',
    'DISPID_SGRClear', 'tagSPPROPERTYINFO', 'DISPID_SBSRead',
    'DISPID_SVEPhoneme', 'DISPID_SpeechPhraseReplacements',
    'eLEXTYPE_PRIVATE7', 'DISPID_SRCPause',
    'DISPID_SREmulateRecognition', 'DISPID_SRCCreateResultFromMemory',
    'eLEXTYPE_USER', 'SPEI_SR_PRIVATE', 'SVSFNLPMask',
    'DISPID_SPIElements', 'SVP_14', 'SVP_8',
    'SAFTCCITT_ALaw_44kHzStereo', 'SpSharedRecoContext',
    'DISPID_SRCVoice', 'SBOPause', 'SpeechGrammarTagWildcard',
    'DISPID_SPPId', 'SpeechVisemeType', 'SPINTERFERENCE', 'SVP_4',
    'SPRS_ACTIVE_WITH_AUTO_PAUSE', 'SPEVENTENUM',
    'SAFTGSM610_44kHzMono', 'DISPID_SOTDataKey', 'STCInprocServer',
    'eLEXTYPE_APP', 'SPSHORTCUTTYPE', 'DISPID_SpeechObjectToken',
    'SVF_Emphasis', 'SpeechCategoryVoices',
    'DISPID_SDKSetBinaryValue', 'DISPID_SVStatus',
    'DISPID_SRCEStartStream', 'SREAllEvents',
    'DISPID_SLAddPronunciation', 'DISPID_SGRSTType', 'SPRS_ACTIVE',
    'SpShortcut', 'DISPID_SOTCategory', 'SVP_1',
    '_ISpeechRecoContextEvents', 'DISPID_SpeechRecoResult2',
    'SpMMAudioOut', 'SPFM_OPEN_READWRITE', 'DISPIDSPTSI_ActiveLength',
    'ISpeechGrammarRules', 'ISpeechPhraseElements',
    'DISPID_SAFSetWaveFormatEx', 'DISPID_SpeechLexiconWords',
    'ISpXMLRecoResult', 'SDA_One_Trailing_Space',
    'DISPID_SDKEnumKeys', 'DISPID_SPIGrammarId', 'DISPID_SPIGetText',
    'SDA_No_Trailing_Space', 'DISPID_SPERetainedSizeBytes',
    'SVEPhoneme', 'DISPID_SRCCmdMaxAlternates', 'SVEAudioLevel',
    'SREStreamEnd', 'SPINTERFERENCE_LATENCY_TRUNCATE_END',
    'SAFTADPCM_22kHzMono', 'DISPID_SWFEFormatTag',
    'DISPID_SVSInputWordLength', 'DISPID_SRGCmdLoadFromFile',
    'DISPID_SVSpeakCompleteEvent', 'DISPID_SAFType',
    'SpeechCategoryAudioOut', 'SPDKL_CurrentConfig',
    'SpeechEmulationCompareFlags', 'SPSMF_SAPI_PROPERTIES',
    'SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE', 'SpeechAudioState',
    'SAFTNonStandardFormat', 'SpeechLexiconType',
    'DISPID_SPEs_NewEnum', 'DISPID_SLWLangId', 'ISpMMSysAudio',
    'DISPID_SVSInputSentencePosition', 'DISPID_SMSGetData',
    'SpPhoneticAlphabetConverter', 'DISPID_SPPParent', 'SPAR_Low',
    'eLEXTYPE_PRIVATE3', 'ISpeechPhoneConverter',
    'DISPID_SRRGetXMLResult', 'ISpeechPhraseProperty',
    'DISPID_SRGDictationSetState', 'SPWORDPRONUNCIATION',
    'DISPID_SPPsItem', 'ISpeechPhraseAlternate',
    'SAFT12kHz8BitStereo', 'SRTReSent',
    'SpeechPropertyLowConfidenceThreshold',
    'DISPID_SRGCmdLoadFromObject', 'SAFT48kHz8BitMono',
    '__MIDL_IWinTypes_0009', 'DISPID_SPRuleParent',
    'DISPID_SVSLastStreamNumberQueued', 'SAFT44kHz16BitMono',
    'DISPID_SRGCmdSetRuleIdState', 'SPRULESTATE',
    'SAFTADPCM_8kHzMono', 'SVSFParseSsml',
    'DISPID_SPEDisplayAttributes', 'SPRS_INACTIVE',
    'DISPID_SRGIsPronounceable', 'SpObjectToken',
    'SREPropertyStringChange', 'SpeechTokenKeyFiles',
    'DISPID_SRGDictationUnload', 'DISPID_SPRNumberOfElements',
    'SAFT8kHz8BitStereo', 'DISPID_SOTGetStorageFileName',
    'SP_VISEME_6', 'DISPID_SRRRecoContext', 'eLEXTYPE_USER_SHORTCUT',
    'ISpeechBaseStream', 'SP_VISEME_4', 'SpeechDataKeyLocation',
    'DISPID_SOTSetId', 'SRSInactiveWithPurge',
    'DISPID_SRCRequestedUIType', 'DISPID_SVPriority',
    'DISPID_SVSLastResult', 'SPEI_HYPOTHESIS', 'DISPID_SRGReset',
    'DISPID_SPAs_NewEnum', 'SECFDefault', 'DISPID_SLWWord', 'SASRun',
    'SPWF_SRENGINE', 'DISPID_SPRuleNumberOfElements',
    'DISPID_SRCERequestUI', 'SpeechDiscardType', 'DISPID_SPPValue',
    'DISPID_SPAsItem', 'SP_VISEME_12', 'SITooFast',
    'SAFT11kHz8BitStereo', 'SPEI_MIN_SR', 'DISPID_SPPs_NewEnum',
    'DISPID_SLGenerationId', 'SDKLCurrentConfig',
    'DISPID_SGRAddResource', 'SAFTCCITT_uLaw_44kHzStereo',
    'SpeechEngineConfidence', 'DISPID_SpeechVoiceEvent',
    '_ISpeechVoiceEvents', 'DISPID_SVPause',
    'SAFTExtendedAudioFormat', 'DISPID_SBSFormat', 'SP_VISEME_17',
    'DISPID_SpeechLexiconWord', 'SVSFIsNotXML', 'SRSInactive',
    'SPPS_SuppressWord', 'DISPID_SVEEnginePrivate',
    'DISPID_SRCRecognizer', 'DISPID_SPRules_NewEnum',
    'SpeechPropertyHighConfidenceThreshold', 'SpeechTokenContext',
    'DISPID_SPIAudioStreamPosition', 'DISPID_SPEAudioSizeBytes',
    'SINoise', 'SPPARTOFSPEECH', 'SpeechAudioFormatGUIDWave',
    'DISPID_SRDisplayUI', 'SpeechRecoProfileProperties',
    'tagSPTEXTSELECTIONINFO', 'DISPID_SpeechPhraseAlternate',
    'DISPID_SPRsItem', 'DISPID_SRSCurrentStreamPosition',
    'SAFT44kHz8BitStereo', 'DISPID_SVGetVoices', 'ISpObjectToken',
    'SpeechMicTraining', 'DISPID_SRCState',
    'DISPID_SRGCmdLoadFromMemory', 'DISPID_SBSSeek',
    'DISPID_SGRSTransitions', 'DISPID_SpeechPhraseReplacement',
    'SAFTCCITT_uLaw_22kHzMono', 'SPADAPTATIONRELEVANCE', 'SPRULE',
    'SPFM_CREATE', 'SPAO_RETAIN_AUDIO', 'SECHighConfidence',
    'ISpeechAudioBufferInfo', 'SVPNormal',
    'SPEI_ACTIVE_CATEGORY_CHANGED', 'ISpProperties',
    'ISpeechPhraseElement', 'DISPID_SPPNumberOfElements',
    'SRTExtendableParse', 'SAFTCCITT_uLaw_8kHzMono',
    'DISPID_SVSLastBookmarkId', 'IEnumSpObjectTokens',
    'SpeechTokenKeyAttributes', 'DISPID_SWFEBlockAlign',
    'SAFT44kHz16BitStereo', 'DISPID_SRRPhraseInfo', 'SPPS_LMA',
    'SINone', 'SP_VISEME_0', 'SPEI_MAX_SR', 'DISPID_SDKEnumValues',
    'DISPID_SABufferInfo', 'DISPID_SASetState',
    'SAFTCCITT_uLaw_22kHzStereo', 'SDTReplacement',
    'DISPID_SLWs_NewEnum', 'DISPID_SVEBookmark',
    'SAFTADPCM_44kHzStereo', 'DISPID_SPPBRestorePhraseFromMemory',
    'DISPID_SRSetPropertyNumber', 'DISPID_SOTCId', 'SGLexical',
    'SPVOICESTATUS', 'SpeechUserTraining', 'SGDisplay',
    'eLEXTYPE_MORPHOLOGY', 'SPSNotOverriden',
    'DISPID_SRCAudioInInterferenceStatus',
    'DISPID_SRCSetAdaptationData', 'ISpPhrase',
    'DISPID_SRCEFalseRecognition', 'DISPID_SPRuleName',
    'SpeechAudioFormatType', 'SVP_13', 'SVSFDefault',
    'DISPID_SRGState', 'SAFTCCITT_uLaw_11kHzMono', 'SPPHRASEPROPERTY',
    'SVP_12', 'SAFT16kHz8BitStereo', 'eLEXTYPE_PRIVATE18',
    'SPPS_Function', '_SPAUDIOSTATE', 'ISpeechRecoResult2',
    'ISpeechGrammarRuleStateTransition', 'DISPID_SLWType',
    'DISPID_SRSetPropertyString', 'ISpeechWaveFormatEx',
    'eWORDTYPE_DELETED', 'SP_VISEME_14', 'ISpRecoCategory',
    'eLEXTYPE_PRIVATE16', 'SGRSTTEpsilon', 'SPEI_REQUEST_UI',
    'SPPS_RESERVED2', 'SAFT16kHz8BitMono',
    'DISPID_SRCERecognizerStateChange', 'SPCT_DICTATION',
    'SAFT48kHz16BitMono', 'SpeechRuleState', 'SPPS_Noun',
    'ISpNotifySource', 'DISPID_SpeechLexiconPronunciation',
    'SPTEXTSELECTIONINFO', 'DISPID_SPEPronunciation',
    'SAFT8kHz16BitStereo', 'ISpNotifySink', 'SAFT11kHz16BitMono',
    'SAFTCCITT_ALaw_8kHzMono', 'DISPID_SRGetFormat', 'SPSHT_Unknown',
    'SAFTTrueSpeech_8kHz1BitMono', 'DISPID_SMSSetData',
    'DISPID_SPPFirstElement', 'SRAImport', 'SPVISEMES', 'SPSNoun',
    'DISPID_SRGSetTextSelection', 'SVESentenceBoundary',
    'DISPID_SpeechVoiceStatus', 'DISPID_SABIBufferSize',
    'DISPID_SVSkip', 'SP_VISEME_2', 'SPEI_MAX_TTS',
    'DISPID_SPCPhoneToId', 'SPEI_RESERVED5',
    'DISPID_SLGetGenerationChange', 'SRCS_Disabled',
    'DISPID_SMSALineId', 'SPWF_INPUT', 'DISPID_SRCEAdaptation',
    'ISpRecoGrammar', 'ISpeechRecoResultTimes',
    'SpUnCompressedLexicon', 'SPPS_Modifier',
    'SpeechCategoryRecognizers', 'SAFT32kHz8BitStereo',
    'DISPID_SPERequiredConfidence', 'SGRSTTWildcard',
    '_RemotableHandle', 'DISPID_SGRName', 'Speech_StreamPos_RealTime',
    'DISPID_SPIGetDisplayAttributes', 'DISPID_SPRuleFirstElement',
    'SRERecoOtherContext', 'SPWP_KNOWN_WORD_PRONOUNCEABLE',
    'DISPID_SOTGetDescription', 'ISpeechPhraseRules',
    'SSFMOpenReadWrite', 'DISPID_SGRsCommit',
    'SAFTCCITT_ALaw_22kHzMono', 'ISpeechXMLRecoResult',
    'SPRS_ACTIVE_USER_DELIMITED', 'SDTDisplayText', 'SDTAlternates',
    'DISPID_SPRuleEngineConfidence', 'DISPID_SRRSetTextFeedback',
    'DISPID_SPACommit', 'SPSFunction', 'DISPID_SPRuleId',
    'SpCustomStream', 'eLEXTYPE_RESERVED7', 'SVEAllEvents',
    'DISPID_SADefaultFormat', 'SPPS_Noncontent',
    'DISPID_SRSClsidEngine', 'DISPID_SGRSAddWordTransition',
    'ISpResourceManager', 'SPSTREAMFORMATTYPE', 'SDTLexicalForm',
    'SPEI_TTS_PRIVATE', 'DISPID_SLPPhoneIds',
    'SPEI_PROPERTY_NUM_CHANGE', 'DISPID_SDKDeleteKey',
    'ISpeechGrammarRuleState', 'SAFT48kHz8BitStereo',
    'DISPID_SGRAddState', 'DISPID_SRRSpeakAudio', 'SPSHT_OTHER',
    'SPEI_RECOGNITION', 'DISPID_SASCurrentDevicePosition',
    'DISPID_SVEventInterests', 'SPSLMA', 'DISPID_SRProfile',
    'SpeechPropertyResourceUsage', 'SPSEMANTICERRORINFO',
    'eLEXTYPE_PRIVATE15',
    'DISPID_SRAllowAudioInputFormatChangesOnNextSet',
    'DISPID_SpeechMemoryStream', 'DISPID_SRGetPropertyNumber',
    'SPLO_STATIC', 'eLEXTYPE_RESERVED8', 'SRAORetainAudio',
    'SAFT22kHz8BitStereo', 'DISPID_SRCESoundEnd', 'SDTRule',
    'SP_VISEME_11', 'ISpeechPhraseInfo', 'SPAR_Medium', 'SVEViseme',
    'SP_VISEME_7', 'SpeechVoiceSpeakFlags', 'IStream',
    'DISPID_SpeechMMSysAudio', 'SSFMCreate', 'ISpeechLexicon',
    'DISPID_SRGetRecognizers', 'SVP_2', 'SRTSMLTimeout',
    'DISPID_SpeechRecoContextEvents', 'ISpeechDataKey',
    'DISPID_SPEDisplayText', 'SP_VISEME_19', 'ISpeechLexiconWord',
    'SPEI_SR_BOOKMARK', 'SPEI_RESERVED2', 'SRERecognition',
    'SPVPRIORITY', 'DISPID_SpeechAudioFormat',
    'DISPID_SRSAudioStatus', 'SVP_6', 'DISPID_SGRSTsItem',
    'DISPID_SPIEnginePrivateData', 'DISPID_SPEsCount', 'SGRSTTRule',
    'DISPID_SABIEventBias', 'SpeechEngineProperties',
    'DISPID_SVSpeakStream', 'SPSERIALIZEDPHRASE',
    'SpeechSpecialTransitionType', 'DISPID_SOTRemove',
    'DISPID_SPRulesCount', 'ISpeechLexiconWords',
    'DISPID_SpeechRecognizerStatus', 'DISPID_SRCRetainedAudio',
    'eLEXTYPE_VENDORLEXICON', 'SpeechVoiceEvents',
    'ISpeechPhraseProperties', 'SpeechRuleAttributes',
    'ISpPhoneConverter', 'SpObjectTokenCategory', 'SPAUDIOBUFFERINFO',
    'SPCT_SUB_COMMAND', 'SpInprocRecognizer', 'SPDATAKEYLOCATION',
    'SPEI_START_SR_STREAM', 'SRSActiveAlways', 'SSSPTRelativeToEnd',
    'SPEI_VOICE_CHANGE', 'DISPID_SASNonBlockingIO', 'SPPS_RESERVED3',
    'DISPID_SRGId', 'DISPID_SWFEBitsPerSample',
    'DISPID_SDKDeleteValue', 'DISPID_SVEVoiceChange',
    'DISPID_SVAllowAudioOuputFormatChangesOnNextSet',
    'SPSHORTCUTPAIR', 'DISPID_SGRsCount', 'SPAR_High',
    'SpMMAudioEnum', 'DISPID_SpeechPhraseProperties', 'SVP_21',
    'DISPID_SRSSupportedLanguages',
    'DISPID_SRAllowVoiceFormatMatchingOnNextSet',
    'SpeechPropertyResponseSpeed', 'DISPID_SOTsCount',
    'SpeechFormatType', 'SPAS_CLOSED', 'DISPID_SVSVisemeId',
    'DISPID_SRCResume', 'SPAS_PAUSE', 'SDKLCurrentUser',
    'ISpStreamFormatConverter', 'eLEXTYPE_PRIVATE20', 'SRSActive',
    'DISPID_SPEsItem', 'SPINTERFERENCE_TOOLOUD',
    'DISPID_SDKGetStringValue', 'DISPID_SRCEPropertyNumberChange',
    'STCLocalServer', 'DISPID_SLAddPronunciationByPhoneIds',
    'DISPID_SpeechGrammarRuleState', 'SpeechRecoContextState',
    'DISPID_SPRuleChildren', 'SPWORDPRONOUNCEABLE',
    'SVSFParseAutodetect', 'eLEXTYPE_PRIVATE2',
    'DISPID_SABufferNotifySize', 'SVP_16', 'DISPID_SPRs_NewEnum',
    'SREPropertyNumChange', 'SLOStatic', 'SPEI_TTS_AUDIO_LEVEL',
    'DISPID_SRRTTickCount', 'DISPID_SLWPronunciations',
    'ISpPhoneticAlphabetConverter', 'SRTEmulated', 'SPEI_UNDEFINED',
    'SpeechRetainedAudioOptions', 'DISPID_SRIsShared',
    'SPGRAMMARWORDTYPE', 'SASPause', 'ISpRecoGrammar2',
    'SpeechAudioVolume', 'DISPID_SpeechObjectTokenCategory',
    'SPEVENT', 'SREAdaptation', 'SRSEDone', 'DISPID_SRCCreateGrammar',
    'DISPID_SPEAudioStreamOffset', 'SPDKL_LocalMachine',
    'DISPID_SPAPhraseInfo', 'SPINTERFERENCE_TOOSLOW', 'SP_VISEME_20',
    'SAFTCCITT_ALaw_8kHzStereo', 'SECFIgnoreKanaType',
    'DISPID_SLPsCount', 'SpeechVoiceSkipTypeSentence',
    'SSFMCreateForWrite', 'SpeechPropertyComplexResponseSpeed',
    'SGLexicalNoSpecialChars', 'SPCS_DISABLED', 'DISPID_SWFEChannels',
    'SAFTText', 'DISPID_SLRemovePronunciationByPhoneIds',
    'SpTextSelectionInformation', 'DISPID_SWFESamplesPerSec',
    'DISPID_SpeechRecoResult', 'DISPID_SDKSetStringValue',
    'SVSFPersistXML', 'SVP_17', 'DISPID_SPEAudioSizeTime',
    'SPBO_PAUSE', 'SPEI_MIN_TTS', 'SPAUDIOSTATUS',
    'SPINTERFERENCE_NOISE', 'eLEXTYPE_PRIVATE6',
    'SAFT32kHz16BitStereo', 'DISPID_SPANumberOfElementsInResult',
    'SVF_None', 'DISPID_SPEAudioTimeOffset', 'SPGS_EXCLUSIVE',
    'SVEVoiceChange', 'DISPID_SGRSAddSpecialTransition',
    'SP_VISEME_21', 'SpeechBookmarkOptions',
    'DISPID_SpeechGrammarRuleStateTransitions', 'SVSFParseSapi',
    'DISPID_SpeechGrammarRules', 'SITooLoud',
    'eLEXTYPE_LETTERTOSOUND', 'SVF_Stressed',
    'SPWT_LEXICAL_NO_SPECIAL_CHARS', 'tagSTATSTG',
    'ISpeechGrammarRule', 'SpPhoneConverter', 'DISPID_SGRsDynamic',
    'SPPHRASEREPLACEMENT', 'eLEXTYPE_RESERVED6', 'SVSFIsFilename',
    'SVPOver', 'ISpVoice', 'SPRST_INACTIVE_WITH_PURGE',
    'DISPID_SVAlertBoundary', 'SPVPRI_NORMAL', 'SPCONTEXTSTATE',
    'DISPID_SLPSymbolic', 'SPRECORESULTTIMES', 'ISpSerializeState',
    'DISPID_SGRInitialState', 'SREPhraseStart', 'SPSInterjection',
    'SpResourceManager', 'SPSMF_SRGS_SEMANTICINTERPRETATION_W3C',
    'SSTTWildcard', 'DISPID_SPIAudioSizeTime', 'DISPID_SPILanguageId',
    'SpeechAddRemoveWord', 'DISPID_SWFEAvgBytesPerSec',
    'SGDSActiveWithAutoPause', 'SRTAutopause', 'DISPID_SPRulesItem',
    'SPPHRASE', 'ISpLexicon', 'SGPronounciation', 'DISPIDSPTSI',
    'SP_VISEME_15', 'DISPID_SRRDiscardResultInfo',
    'DISPID_SpeechBaseStream', 'DISPID_SGRSAddRuleTransition',
    'SAFTCCITT_ALaw_11kHzStereo', 'SPSMF_UPS', 'ISpeechVoice',
    'SAFTCCITT_ALaw_11kHzMono', 'DISPID_SPAStartElementInResult',
    'SpeechVoicePriority', 'SRESoundEnd', 'DISPID_SVEAudioLevel',
    'SPEI_SR_AUDIO_LEVEL', 'DISPID_SAEventHandle', 'SITooSlow',
    'SPSHT_EMAIL', 'SPEI_PHRASE_START', 'SPFM_OPEN_READONLY',
    'SPPS_NotOverriden', 'SPWP_UNKNOWN_WORD_PRONOUNCEABLE',
    'SAFT44kHz8BitMono', 'DISPID_SRGetPropertyString', 'SREBookmark',
    'ISpeechRecognizer', 'DISPID_SPRText',
    'SAFTCCITT_ALaw_22kHzStereo', 'typelib_path',
    'SAFTCCITT_uLaw_8kHzStereo', 'DISPID_SLWsItem',
    'DISPID_SRGSetWordSequenceData', 'SPEI_END_SR_STREAM',
    'SPRST_ACTIVE', 'SSTTTextBuffer', 'DISPID_SRCEAudioLevel',
    'SAFT11kHz16BitStereo', 'SAFT22kHz16BitMono',
    'SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN', 'SpSharedRecognizer',
    'DISPID_SPARecoResult', 'DISPID_SpeechPhraseElements',
    'SAFT24kHz8BitStereo', 'SpeechCategoryRecoProfiles',
    'SpeechGrammarWordType', 'ISpeechTextSelectionInformation',
    'DISPID_SPELexicalForm', 'SPCS_ENABLED'
]

