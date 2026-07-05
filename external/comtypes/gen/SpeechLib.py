from enum import IntFlag

import comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 as __wrapper_module__
from comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 import (
    SPGS_ENABLED, SpMMAudioEnum, WAVEFORMATEX, _FILETIME,
    ISpeechRecoContext, SREFalseRecognition, SLOStatic,
    DISPID_SVEventInterests, SPEI_FALSE_RECOGNITION, SREBookmark,
    SRADefaultToActive, ISpeechPhraseElements, ISpNotifyTranslator,
    SASPause, DISPID_SPRulesCount, SDA_Consume_Leading_Spaces,
    DISPID_SOTGetStorageFileName, DISPID_SVWaitUntilDone,
    SGRSTTDictation, DISPID_SLWsCount, SpeechTokenKeyAttributes,
    DISPID_SAStatus, DISPID_SPPEngineConfidence,
    DISPID_SVSInputWordPosition, DISPID_SOTSetId, WSTRING,
    ISpRecoResult, DISPID_SPEActualConfidence, SAFT32kHz8BitMono,
    DISPID_SDKSetLongValue, SPFM_CREATE_ALWAYS, SAFT22kHz16BitStereo,
    SPEI_MAX_SR, DISPID_SPIAudioSizeBytes, SITooSlow,
    SAFTCCITT_ALaw_11kHzStereo, SpNotifyTranslator, DISPID_SOTDataKey,
    DISPID_SRGIsPronounceable, SpeechEngineProperties,
    DISPID_SGRSTsCount, SGRSTTWord, SVP_0, DISPID_SGRsCommit,
    SPEI_VOICE_CHANGE, SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE,
    SPDKL_CurrentUser, eWORDTYPE_ADDED, SVEStartInputStream,
    SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN, SVP_13, ISpResourceManager,
    SECFIgnoreKanaType, DISPID_SPERetainedSizeBytes,
    DISPID_SRGRecoContext, SDKLDefaultLocation, SREPhraseStart,
    SAFTCCITT_ALaw_22kHzMono, DISPID_SCSBaseStream, SDTReplacement,
    DISPID_SRSCurrentStreamPosition, SDKLCurrentUser, SVF_None,
    SPEI_RESERVED2, DISPID_SRRTLength, SGRSTTRule,
    ISpeechCustomStream, wireHWND, SREStreamEnd, SAFT12kHz16BitMono,
    ISpeechPhraseReplacement, SVP_3, CoClass,
    SAFTCCITT_uLaw_11kHzStereo, SpSharedRecoContext,
    SECNormalConfidence, ISpeechLexiconWord,
    DISPID_SVSyncronousSpeakTimeout, DISPID_SPPName,
    DISPID_SVSpeakCompleteEvent, ISpLexicon, SVP_7,
    SPFM_OPEN_READONLY, SVSFPersistXML, SREStreamStart,
    SpeechGrammarTagWildcard, SpeechVoiceCategoryTTSRate,
    DISPID_SPRuleNumberOfElements, SDTAlternates, eLEXTYPE_PRIVATE19,
    SpFileStream, DISPID_SRCEPhraseStart, SPPS_Unknown,
    DISPID_SRGCmdLoadFromObject, SPBO_PAUSE, DISPID_SGRsAdd, GUID,
    SVSFNLPSpeakPunc, ISpDataKey, DISPID_SVGetAudioOutputs,
    DISPID_SRGDictationUnload, SSSPTRelativeToStart,
    SpeechTokenValueCLSID, SAFT32kHz16BitMono, SPEI_SOUND_END,
    SAFTNonStandardFormat, SRARoot, DISPID_SPCPhoneToId,
    SRESoundStart, SPSMF_UPS, SPSEMANTICERRORINFO, SP_VISEME_19,
    DISPID_SRGetPropertyNumber, SPSHT_NotOverriden,
    SECFNoSpecialChars, SSFMCreateForWrite, SPCS_DISABLED,
    SP_VISEME_3, SAFTADPCM_22kHzMono, DISPID_SPPsItem, SVSFIsFilename,
    DISPID_SMSADeviceId, SREAudioLevel, DISPID_SAVolume,
    DISPID_SRRTTickCount, DISPID_SRGCmdLoadFromMemory, SPCS_ENABLED,
    DISPID_SWFEExtraData, DISPID_SGRSTs_NewEnum,
    DISPID_SVSInputSentencePosition, SPAR_Medium, SVP_17,
    SPEI_END_SR_STREAM, DISPID_SVESentenceBoundary,
    DISPID_SPRuleParent, SRERequestUI, DISPID_SVVolume,
    SAFT11kHz16BitStereo, ISpeechAudioFormat, SAFT44kHz16BitMono,
    SAFT32kHz16BitStereo, ISpeechObjectToken, DISPMETHOD,
    DISPID_SVAllowAudioOuputFormatChangesOnNextSet, DISPID_SASetState,
    DISPID_SPEsCount, ISpeechRecoResult2,
    DISPID_SRCEPropertyStringChange, SPVPRI_ALERT, SPSHORTCUTPAIRLIST,
    SECLowConfidence, DISPID_SRGState, SP_VISEME_4, DISPID_SMSGetData,
    DISPID_SRCVoicePurgeEvent, DISPID_SRCEAdaptation, SDTLexicalForm,
    SPAUDIOBUFFERINFO, SVEAudioLevel, SP_VISEME_17,
    SPEI_SR_AUDIO_LEVEL, SPEI_SOUND_START,
    DISPID_SVSLastStreamNumberQueued, DISPID_SPIElements,
    IEnumSpObjectTokens, Speech_Default_Weight, SRADynamic,
    DISPID_SGRId, SGSEnabled, SpStream, SRERecognition,
    DISPID_SWFEFormatTag, SITooQuiet, ISpRecognizer3,
    DISPID_SDKEnumKeys, SFTInput, SpPhoneticAlphabetConverter,
    SAFT16kHz16BitStereo, ISpeechLexiconPronunciation, _check_version,
    SAFT11kHz16BitMono, DISPID_SRCreateRecoContext,
    SpTextSelectionInformation, SpPhraseInfoBuilder, SRAORetainAudio,
    eLEXTYPE_RESERVED4, DISPID_SRCEEnginePrivate, ISpeechRecognizer,
    SAFTNoAssignedFormat, ISpRecognizer2, SAFT22kHz8BitMono,
    DISPID_SABufferNotifySize, DISPID_SVEStreamStart,
    DISPID_SPPsCount, eLEXTYPE_PRIVATE8, SVP_2,
    SAFTCCITT_uLaw_11kHzMono, ISpeechPhraseInfoBuilder, SLTApp,
    ISpRecoGrammar, SGDSActive, DISPID_SPAPhraseInfo,
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS, DISPID_SRCEventInterests,
    SpeechRegistryUserRoot, ISpeechGrammarRuleStateTransition,
    ULONG_PTR, SpeechGrammarTagDictation,
    DISPID_SLRemovePronunciationByPhoneIds, ISpeechAudioBufferInfo,
    SLODynamic, SVP_1, ISpGrammarBuilder, DISPID_SPIProperties,
    SpeechCategoryRecoProfiles, SpAudioFormat, SVSFVoiceMask, SPEVENT,
    SPGS_DISABLED, DISPID_SPRuleId, DISPID_SOTCreateInstance,
    SP_VISEME_7, DISPID_SLWWord, ISpeechLexiconPronunciations,
    DISPID_SVSRunningState, DISPID_SMSSetData, SRAONone,
    SVSFlagsAsync, DISPID_SOTCEnumerateTokens,
    SPEI_PROPERTY_STRING_CHANGE, SREPropertyNumChange, DISPID_SGRName,
    ISpPhoneConverter, SPPS_Verb, ISpRecoGrammar2,
    ISpeechLexiconWords, DISPID_SRGDictationSetState,
    ISequentialStream, SpeechGrammarTagUnlimitedDictation,
    DISPID_SLGenerationId, DISPID_SABIMinNotification, SVP_6,
    DISPID_SRGSetTextSelection, DISPID_SVIsUISupported,
    SAFTCCITT_uLaw_44kHzMono, DISPID_SOTDisplayUI, SAFT8kHz8BitMono,
    DISPID_SRGReset, SRTExtendableParse, SVP_8, SP_VISEME_5,
    SAFT8kHz16BitMono, ISpeechBaseStream, DISPID_SVEBookmark,
    DISPID_SLAddPronunciationByPhoneIds, SAFTGSM610_8kHzMono,
    SRSActiveAlways, DISPID_SGRClear, SAFTADPCM_22kHzStereo,
    DISPID_SRRRecoContext, SPPHRASEPROPERTY, SPPS_RESERVED4,
    ISpeechPhraseReplacements, ISpeechMMSysAudio, DISPID_SOTCId,
    SASStop, DISPID_SRGDictationLoad, SREAdaptation,
    eLEXTYPE_PRIVATE9, SAFT48kHz8BitMono, DISPID_SPRFirstElement,
    SPPHRASE, SPVPRI_NORMAL, DISPID_SPPChildren, SPEI_SR_BOOKMARK,
    SPINTERFERENCE_TOOQUIET, SpPhoneConverter, SPDKL_LocalMachine,
    DISPID_SRCEStartStream, SPAS_PAUSE, DISPID_SVEAudioLevel,
    SDA_No_Trailing_Space, SPCT_SLEEP, DISPID_SVRate,
    SPCT_SUB_COMMAND, ISpAudio, SAFT48kHz8BitStereo, SpeechTokenKeyUI,
    SAFTCCITT_uLaw_8kHzMono, SASRun, ISpeechPhraseRule,
    SDTPronunciation, SAFTCCITT_ALaw_8kHzMono,
    DISPID_SRGCmdLoadFromFile, SPGS_EXCLUSIVE,
    DISPID_SPRuleFirstElement, eLEXTYPE_PRIVATE18, SPEI_RESERVED5,
    SDKLCurrentConfig, SAFT16kHz16BitMono, SpeechCategoryRecognizers,
    DISPID_SRCEFalseRecognition, ISpeechPhraseElement,
    ISpeechAudioStatus, SAFT48kHz16BitMono, SAFTCCITT_ALaw_8kHzStereo,
    IEnumString, SPINTERFERENCE_TOOLOUD, DISPID_SBSFormat,
    DISPID_SRSCurrentStreamNumber, _ISpeechVoiceEvents,
    DISPID_SLPSymbolic, ISpeechRecoResultTimes, SPSERIALIZEDRESULT,
    SpeechPropertyAdaptationOn, DISPID_SRSNumberOfActiveRules,
    DISPID_SPCIdToPhone, SpeechPropertyResourceUsage, SPWORDLIST,
    STCRemoteServer, SPSHORTCUTPAIR, SpeechAudioFormatGUIDText,
    SPEI_SR_RETAINEDAUDIO, DISPID_SDKDeleteValue,
    SPINTERFERENCE_NOSIGNAL, STSF_LocalAppData, SAFTDefault,
    eLEXTYPE_APP, DISPID_SRCRetainedAudio, SPFM_CREATE, SPRST_ACTIVE,
    SPXRO_Alternates_SML, DISPID_SRCESoundStart, DISPID_SPIGetText,
    DISPID_SOTRemove, ISpStreamFormatConverter, SAFT12kHz8BitMono,
    DISPID_SOTCSetId, DISPID_SLWsItem, SPEI_MAX_TTS, SGRSTTWildcard,
    SPAO_RETAIN_AUDIO, SpMemoryStream, SP_VISEME_20,
    DISPID_SDKGetStringValue, SAFTText, _ULARGE_INTEGER, SWTDeleted,
    DISPID_SVSLastBookmarkId, DISPID_SVEStreamEnd,
    SPRST_ACTIVE_ALWAYS, SAFT24kHz16BitMono, ISpXMLRecoResult,
    SPEI_RESERVED1, SVP_11, SpUnCompressedLexicon,
    DISPID_SPEDisplayAttributes, DISPID_SAFType, SPINTERFERENCE_NONE,
    SPEI_START_SR_STREAM, SWPUnknownWordPronounceable,
    SPINTERFERENCE_TOOFAST, DISPID_SRRDiscardResultInfo,
    DISPID_SRCERecognitionForOtherContext, SpInprocRecognizer,
    DISPID_SRRSaveToMemory, SVSFParseAutodetect, SPLO_DYNAMIC,
    DISPID_SRSetPropertyNumber, ISpeechPhraseProperties,
    DISPID_SLPPhoneIds, SVEPrivate, DISPID_SRAudioInput,
    eLEXTYPE_RESERVED10, DISPID_SPPBRestorePhraseFromMemory,
    SSFMOpenReadWrite, SRSEDone, DISPID_SPAStartElementInResult,
    SVEPhoneme, DISPID_SGRAddState, DISPID_SRGCmdSetRuleIdState,
    DISPID_SPIStartTime, DISPID_SPRs_NewEnum, DISPID_SGRAddResource,
    IServiceProvider, DISPID_SRCERequestUI, DISPID_SPARecoResult,
    SAFT32kHz8BitStereo, DISPID_SRCEPropertyNumberChange,
    DISPID_SRCESoundEnd, DISPID_SPIAudioSizeTime, DISPID_SLGetWords,
    helpstring, DISPID_SRProfile, DISPID_SLPs_NewEnum, SBOPause,
    SVSFIsXML, eLEXTYPE_PRIVATE3, SPRST_INACTIVE_WITH_PURGE,
    DISPID_SVAudioOutput, HRESULT, DISPID_SRIsShared, DISPID_SASState,
    STCAll, SVEAllEvents, DISPID_SVGetAudioInputs, tagSTATSTG,
    SSTTDictation, SVSFDefault, IInternetSecurityMgrSite,
    DISPID_SRRAlternates, SAFT11kHz8BitStereo, ISpeechPhraseInfo,
    SPBO_AHEAD, DISPID_SLPType, SITooFast, DISPID_SBSSeek,
    SAFT24kHz8BitStereo, DISPID_SVSpeakStream,
    SAFTCCITT_uLaw_22kHzStereo, SPEI_SENTENCE_BOUNDARY, SPAS_CLOSED,
    eLEXTYPE_PRIVATE15, DISPID_SASCurrentSeekPosition, SVP_4,
    DISPID_SPANumberOfElementsInResult, SGLexical,
    DISPID_SASFreeBufferSpace, SRTSMLTimeout, SPXRO_SML, ISpeechVoice,
    ISpRecognizer, SVF_Stressed, eLEXTYPE_PRIVATE17,
    SPEI_INTERFERENCE, DISPID_SGRSTPropertyValue, ISpeechVoiceStatus,
    DISPID_SDKSetStringValue, SpResourceManager, ISpMMSysAudio,
    DISPID_SGRSTWeight, SPSLMA, DISPID_SRRGetXMLErrorInfo,
    SPCT_SUB_DICTATION, DISPID_SPIRule, ISpRecoContext2, SRESoundEnd,
    SPBO_TIME_UNITS, ISpPhrase, DISPID_SPELexicalForm,
    DISPID_SPERequiredConfidence, DISPID_SPRText, SAFT8kHz16BitStereo,
    ISpEventSource, SAFT12kHz16BitStereo, DISPID_SRSAudioStatus,
    SVESentenceBoundary, SAFT22kHz16BitMono,
    DISPID_SOTRemoveStorageFileName, SpeechRegistryLocalMachineRoot,
    DISPID_SPIReplacements, SECFIgnoreWidth, SVP_10, SPEI_ADAPTATION,
    SPSSuppressWord, SVEWordBoundary, SAFTADPCM_8kHzMono,
    SpeechPropertyLowConfidenceThreshold, DISPID_SDKCreateKey,
    eLEXTYPE_USER, DISPID_SAFGuid, eLEXTYPE_RESERVED7,
    SPBINARYGRAMMAR, ISpObjectToken, SPRECORESULTTIMES, SSTTWildcard,
    DISPID_SPEsItem, DISPIDSPTSI_ActiveOffset,
    DISPID_SRAudioInputStream, SP_VISEME_15, SPPS_RESERVED3,
    DISPID_SRGCmdSetRuleState, DISPID_SDKDeleteKey,
    SGLexicalNoSpecialChars, DISPID_SRCEAudioLevel,
    ISpeechGrammarRule, SSTTTextBuffer, DISPID_SRGetRecognizers,
    SpWaveFormatEx, SPRS_INACTIVE,
    SPINTERFERENCE_LATENCY_TRUNCATE_END, SAFTCCITT_ALaw_22kHzStereo,
    DISPID_SPRsItem, SDTAll, eLEXTYPE_PRIVATE12,
    SAFTCCITT_uLaw_44kHzStereo, SAFTGSM610_11kHzMono, SPAS_STOP,
    SAFTCCITT_uLaw_8kHzStereo, SWPUnknownWordUnpronounceable,
    SDTProperty, DISPID_SPEAudioTimeOffset, SAFT44kHz8BitStereo,
    SRCS_Enabled, SpeechMicTraining, SP_VISEME_2,
    SAFT24kHz16BitStereo, DISPID_SOTGetAttribute, SVSFIsNotXML,
    DISPID_SPRules_NewEnum, DISPID_SPIEngineId, SREStateChange,
    DISPID_SGRSTNextState, _ISpeechRecoContextEvents,
    DISPID_SLWs_NewEnum, DISPID_SPILanguageId, SPBO_NONE,
    SAFT16kHz8BitMono, SRCS_Disabled, ISpeechPhraseRules,
    SpeechAddRemoveWord, SPSVerb, SPSMF_SRGS_SAPIPROPERTIES,
    SPINTERFERENCE_LATENCY_WARNING, DISPID_SRGetPropertyString,
    DISPID_SGRsDynamic, ISpEventSink, DISPID_SRCERecognition,
    SGRSTTEpsilon, SRSEIsSpeaking, SPEI_RECO_OTHER_CONTEXT,
    DISPID_SWFESamplesPerSec, DISPID_SVSVisemeId,
    __MIDL___MIDL_itf_sapi_0000_0020_0002, DISPID_SAFGetWaveFormatEx,
    tagSPTEXTSELECTIONINFO, SpLexicon, ISpeechPhraseProperty,
    SPEI_REQUEST_UI, DISPID_SGRInitialState, SPPHRASEREPLACEMENT,
    SPWP_KNOWN_WORD_PRONOUNCEABLE, DISPID_SDKOpenKey,
    Speech_StreamPos_Asap, SPAUDIOSTATUS, SAFTCCITT_ALaw_44kHzStereo,
    SPEI_RESERVED6, DISPID_SPIGetDisplayAttributes, SRTReSent,
    SWPKnownWordPronounceable, DISPID_SPPId, eLEXTYPE_PRIVATE7,
    DISPID_SPIEnginePrivateData, IStream, DISPID_SRDisplayUI,
    SPPS_RESERVED1, VARIANT_BOOL, DISPID_SABIBufferSize,
    eLEXTYPE_USER_SHORTCUT, SPAR_Low, SDTAudio,
    DISPID_SDKSetBinaryValue, SINoise, ISpNotifySource, SPLO_STATIC,
    IInternetSecurityManager, DISPID_SPRuleChildren, DISPID_SPACommit,
    SpVoice, DISPID_SRIsUISupported, SGRSTTTextBuffer,
    DISPID_SPPValue, DISPID_SPISaveToMemory, SPEI_SR_PRIVATE,
    DISPID_SRAllowVoiceFormatMatchingOnNextSet,
    DISPID_SDKGetBinaryValue, SPDKL_DefaultLocation,
    ISpeechGrammarRuleState, SPPROPERTYINFO, dispid, SVP_9,
    DISPID_SRCRetainedAudioFormat, SRTStandard, SPFM_OPEN_READWRITE,
    SP_VISEME_13, _RemotableHandle, SPRECOGNIZERSTATUS,
    DISPID_SRRSpeakAudio, SPCT_COMMAND, DISPID_SLPsCount,
    SPEI_TTS_AUDIO_LEVEL, SPSNoun, BSTR, SPWT_DISPLAY,
    ISpeechTextSelectionInformation, DISPID_SRSSupportedLanguages,
    ISpeechRecoResult, SAFTCCITT_ALaw_11kHzMono, DISPID_SVGetVoices,
    SpeechRecoProfileProperties, SP_VISEME_18,
    DISPID_SPIRetainedSizeBytes, DISPID_SGRSAddWordTransition,
    DISPID_SVSInputSentenceLength, SPEI_HYPOTHESIS, SVP_20,
    SREHypothesis, DISPID_SLPLangId, SAFTGSM610_44kHzMono,
    SPTEXTSELECTIONINFO, DISPID_SPRuleEngineConfidence, SPWORD,
    DISPID_SOTCDefault, DISPID_SRRPhraseInfo, SAFT12kHz8BitStereo,
    SPDKL_CurrentConfig, DISPID_SRRAudioFormat, SVF_Emphasis,
    SPPS_Function, DISPID_SLWPronunciations,
    DISPID_SRCERecognizerStateChange, DISPID_SPEAudioStreamOffset,
    SVPNormal, DISPID_SBSWrite, SGSExclusive, SPAR_High,
    SAFTADPCM_8kHzStereo, DISPID_SVEEnginePrivate, eLEXTYPE_PRIVATE20,
    DISPID_SABufferInfo, DISPID_SVPause, SECFIgnoreCase, SVPOver,
    SVEBookmark, SPEI_TTS_BOOKMARK, typelib_path, SRAImport,
    SPWORDPRONUNCIATION, SPPS_SuppressWord, SRTAutopause, SPEI_VISEME,
    SVP_19, ISpeechMemoryStream, ISpeechGrammarRules,
    SDA_One_Trailing_Space, DISPID_SGRSRule, DISPID_SRGetFormat,
    SpeechDictationTopicSpelling, SpObjectToken, SpeechAudioVolume,
    SpeechUserTraining, DISPID_SVSLastResult, ISpObjectTokenCategory,
    eLEXTYPE_PRIVATE16, SAFT48kHz16BitStereo, VARIANT, SVEVoiceChange,
    DISPID_SMSALineId, SRSInactiveWithPurge, SPINTERFERENCE_TOOSLOW,
    SP_VISEME_6, DISPID_SRCEBookmark, ISpeechPhraseAlternate,
    ISpeechDataKey, SP_VISEME_9, ISpeechPhraseAlternates, SPSModifier,
    SASClosed, DISPID_SWFEBlockAlign, DISPID_SLPsItem,
    DISPID_SOTsCount, SSFMCreate, DISPID_SAFSetWaveFormatEx,
    SpMMAudioIn, DISPID_SPEDisplayText, DISPID_SPRuleName,
    DISPID_SOTGetDescription, SVSFPurgeBeforeSpeak,
    DISPID_SOTs_NewEnum, SAFT11kHz8BitMono, ISpStreamFormat,
    DISPIDSPTSI_SelectionOffset, SVSFParseSapi, DISPID_SBSRead,
    SpeechAudioProperties, SAFTADPCM_44kHzStereo,
    DISPID_SRGSetWordSequenceData, SAFTCCITT_ALaw_44kHzMono,
    SRATopLevel, SpeechVoiceSkipTypeSentence, __MIDL_IWinTypes_0009,
    SREPropertyStringChange, DISPID_SGRSTText,
    DISPID_SOTIsUISupported, SPRS_ACTIVE, eLEXTYPE_RESERVED6,
    SPEI_MIN_TTS, SGSDisabled, SPWF_INPUT, SPSERIALIZEDPHRASE,
    DISPID_SGRSTransitions, DISPID_SOTMatchesAttributes,
    SPWF_SRENGINE, SPSHT_OTHER, SPVOICESTATUS,
    DISPID_SRCSetAdaptationData, DISPID_SOTsItem,
    DISPID_SGRSTPropertyName, DISPID_SVEVoiceChange, DISPID_SRCState,
    DISPID_SRCBookmark, SPEVENTSOURCEINFO, SPEI_UNDEFINED,
    STCLocalServer, SPPS_LMA, DISPID_SPAs_NewEnum,
    SpeechTokenIdUserLexicon, DISPID_SFSClose, ISpeechRecoGrammar,
    eLEXTYPE_PRIVATE1, DISPID_SGRs_NewEnum, LONG_PTR, SVP_18,
    DISPID_SPAsItem, SREPrivate, DISPID_SDKEnumValues,
    SGDSActiveWithAutoPause, DISPID_SRCRequestedUIType,
    SPEI_START_INPUT_STREAM, SRTEmulated, eLEXTYPE_LETTERTOSOUND,
    SVSFUnusedFlags, SGDSActiveUserDelimited, SWTAdded,
    DISPID_SVEWord, DISPID_SPRDisplayAttributes,
    SpeechCategoryAudioIn, ISpSerializeState, SECFDefault, SVP_12,
    SpeechAudioFormatGUIDWave, eLEXTYPE_PRIVATE6, SVP_16,
    DISPID_SPRNumberOfElements, ISpeechRecognizerStatus,
    SPSHT_Unknown, DISPID_SRCRecognizer, STCInprocServer,
    SpeechTokenKeyFiles, SAFT44kHz8BitMono, DISPID_SRRTStreamTime,
    DISPID_SWFEAvgBytesPerSec, SAFTADPCM_11kHzMono,
    DISPID_SAEventHandle, SPEI_RECOGNITION,
    DISPID_SRCCmdMaxAlternates, DISPID_SPERetainedStreamOffset,
    DISPID_SVEViseme, DISPID_SRCCreateGrammar, SVP_21, SPRST_INACTIVE,
    DISPID_SASNonBlockingIO, DISPID_SGRSTType,
    SpeechPropertyHighConfidenceThreshold, eLEXTYPE_PRIVATE4,
    DISPID_SPAsCount, SpSharedRecognizer, DISPID_SREmulateRecognition,
    SECHighConfidence, DISPID_SLRemovePronunciation,
    DISPID_SGRSTsItem, SGPronounciation, DISPID_SPRsCount,
    ISpeechPhoneConverter, SVSFParseMask, SpCustomStream,
    ISpeechLexicon, DISPID_SGRAttributes, tagSPPROPERTYINFO,
    SpInProcRecoContext, SECFEmulateResult, ISpProperties,
    DISPIDSPTSI_SelectionLength, DISPID_SGRsCount,
    DISPID_SABIEventBias, DISPID_SPPParent, SPEI_RESERVED3,
    SPPS_Interjection, SPSMF_SRGS_SEMANTICINTERPRETATION_W3C,
    SPRECOCONTEXTSTATUS, SPRS_ACTIVE_WITH_AUTO_PAUSE,
    DISPID_SPIGrammarId, SFTSREngine, DISPID_SGRsCommitAndSave,
    SP_VISEME_14, DISPID_SVPriority, DISPID_SRState,
    DISPID_SRSClsidEngine, SpeechCategoryVoices, SRAInterpreter,
    ISpPhoneticAlphabetConverter, DISPID_SVGetProfiles,
    SPWT_LEXICAL_NO_SPECIAL_CHARS, SBONone, STSF_AppData,
    SPPS_Noncontent, DISPID_SDKGetlongValue, ISpeechXMLRecoResult,
    SPEI_WORD_BOUNDARY, DISPID_SRCCreateResultFromMemory, _lcid,
    DISPID_SLWLangId, DISPID_SOTCategory,
    DISPID_SASCurrentDevicePosition, SGDisplay,
    DISPID_SVSInputWordLength, SPEI_MIN_SR, SPPS_NotOverriden,
    SAFT16kHz8BitStereo, DISPID_SWFEChannels, SpeechAllElements,
    SPPS_Noun, DISPID_SPEAudioSizeBytes, SVSFNLPMask,
    SPWP_UNKNOWN_WORD_PRONOUNCEABLE, DISPID_SPIAudioStreamPosition,
    DISPID_SPPConfidence, SP_VISEME_11, SpObjectTokenCategory,
    Speech_Max_Word_Length, DISPID_SVAlertBoundary, DISPID_SRRTimes,
    DISPID_SGRSTPropertyId, SPPHRASEELEMENT, SINoSignal, SP_VISEME_10,
    DISPID_SVSPhonemeId, DISPID_SLGetGenerationChange,
    SPEI_END_INPUT_STREAM, DISPID_SRSetPropertyString,
    DISPID_SRStatus, SpStreamFormatConverter, DISPID_SGRsItem,
    DISPID_SLGetPronunciations, _LARGE_INTEGER, SPEI_PHRASE_START,
    SPFM_NUM_MODES, DISPID_SVAudioOutputStream, STSF_FlagCreate,
    SP_VISEME_16, ISpPhoneticAlphabetSelection, DISPID_SPCLangId,
    SPSHT_EMAIL, DISPID_SRCEHypothesis, SPRST_NUM_STATES,
    eLEXTYPE_MORPHOLOGY, SVP_14, SPPS_Modifier, SDKLLocalMachine,
    SP_VISEME_21, DISPID_SRCEEndStream, DISPID_SFSOpen, SRSActive,
    ISpRecoContext, ISpObjectWithToken, SAFT8kHz8BitStereo,
    eLEXTYPE_PRIVATE14, SVSFParseSsml, SRERecoOtherContext,
    SAFT24kHz8BitMono, DISPID_SGRsFindRule, COMMETHOD,
    DISPID_SPPNumberOfElements,
    DISPID_SRGCmdLoadFromProprietaryGrammar,
    DISPID_SGRSAddSpecialTransition, DISPID_SWFEBitsPerSample,
    DISPID_SRRTOffsetFromStart, SAFT22kHz8BitStereo,
    SpeechCategoryAudioOut, DISPID_SVDisplayUI, DISPID_SRRAudio,
    DISPID_SLPPartOfSpeech, SpeechPropertyNormalConfidenceThreshold,
    DISPID_SVVoice, SITooLoud, SAFTADPCM_44kHzMono, ISpRecoCategory,
    eLEXTYPE_PRIVATE2, DISPID_SLAddPronunciation, eLEXTYPE_RESERVED9,
    ISpPhraseAlt, Library, SpNullPhoneConverter, ISpeechObjectTokens,
    DISPID_SVResume, SAFTExtendedAudioFormat,
    SPEI_ACTIVE_CATEGORY_CHANGED, SpeechPropertyComplexResponseSpeed,
    SPSMF_SAPI_PROPERTIES, SP_VISEME_12, DISPID_SVStatus, SPAS_RUN,
    SVP_5, DISPID_SRRGetXMLResult, DISPID_SPRulesItem,
    SPEI_TTS_PRIVATE, SP_VISEME_0, SPWT_LEXICAL,
    SSSPTRelativeToCurrentPosition, SPPS_RESERVED2, SpShortcut,
    UINT_PTR, SPSFunction, DISPID_SPPFirstElement, SPWT_PRONUNCIATION,
    DISPID_SRCResume, SAFTADPCM_11kHzStereo, SGDSInactive,
    SVEEndInputStream, SPEI_PHONEME, SAFTCCITT_uLaw_22kHzMono,
    SPVPRI_OVER, DISPID_SRRSetTextFeedback, eLEXTYPE_PRIVATE13,
    DISPID_SPEPronunciation, SAFT44kHz16BitStereo, DISPID_SRGId,
    DISPID_SGRSAddRuleTransition, SDA_Two_Trailing_Spaces,
    SpeechPropertyResponseSpeed, DISPID_SRCAudioInInterferenceStatus,
    SAFTTrueSpeech_8kHz1BitMono, Speech_Max_Pron_Length,
    SPWORDPRONUNCIATIONLIST, SPCT_DICTATION,
    SpeechCategoryPhoneConverters, SPINTERFERENCE_NOISE,
    DISPID_SPPs_NewEnum, DISPID_SGRSTRule, SPRS_ACTIVE_USER_DELIMITED,
    __MIDL___MIDL_itf_sapi_0000_0020_0001, SDTDisplayText,
    ISpeechGrammarRuleStateTransitions, SINone, SpCompressedLexicon,
    SpMMAudioOut, SVPAlert, DISPID_SVSCurrentStreamNumber,
    DISPID_SPEs_NewEnum, SAFTGSM610_22kHzMono, SSFMOpenForRead,
    DISPID_SLWType, DISPID_SRAllowAudioInputFormatChangesOnNextSet,
    DISPID_SOTId, SpeechCategoryAppLexicons,
    DISPID_SPEEngineConfidence, DISPID_SPRuleConfidence, IUnknown,
    DISPID_SRGCmdLoadFromResource, SRSInactive, DISPID_SRCVoice,
    ISpeechFileStream, SDTRule, DISPID_SOTCGetDataKey, ISpStream,
    ISpeechRecoResultDispatch, DISPID_SRCEInterference, SRAExport,
    DISPID_SRCPause, DISPID_SRRecognizer, SPEI_PROPERTY_NUM_CHANGE,
    SPEI_RECO_STATE_CHANGE, eLEXTYPE_RESERVED8, STSF_CommonAppData,
    DISPID_SVSkip, Speech_StreamPos_RealTime, DISPID_SVSLastBookmark,
    SPSInterjection, SREAllEvents, ISpeechObjectTokenCategory,
    SPAR_Unknown, DISPID_SVSpeak, DISPID_SPEAudioSizeTime,
    DISPID_SRGRules, ISpeechResourceLoader, SPPHRASERULE, ISpVoice,
    SVEViseme, SPRULE, SP_VISEME_8, DISPID_SADefaultFormat,
    eWORDTYPE_DELETED, DISPIDSPTSI_ActiveLength, SPSNotOverriden,
    SPSUnknown, SLTUser, eLEXTYPE_PRIVATE5, DISPID_SVEPhoneme,
    ISpShortcut, eLEXTYPE_VENDORLEXICON, SSSPTRelativeToEnd,
    SREInterference, ISpNotifySink, ISpeechAudio, STCInprocHandler,
    eLEXTYPE_PRIVATE11, DISPID_SMSAMMHandle, SPAO_NONE,
    ISpeechWaveFormatEx, SVP_15, DISPID_SRGCommit, SP_VISEME_1,
    eLEXTYPE_PRIVATE10
)


class SPWORDPRONOUNCEABLE(IntFlag):
    SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE = 0
    SPWP_UNKNOWN_WORD_PRONOUNCEABLE = 1
    SPWP_KNOWN_WORD_PRONOUNCEABLE = 2


class SPGRAMMARSTATE(IntFlag):
    SPGS_DISABLED = 0
    SPGS_ENABLED = 1
    SPGS_EXCLUSIVE = 3


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


class SPGRAMMARWORDTYPE(IntFlag):
    SPWT_DISPLAY = 0
    SPWT_LEXICAL = 1
    SPWT_PRONUNCIATION = 2
    SPWT_LEXICAL_NO_SPECIAL_CHARS = 3


class SPAUDIOOPTIONS(IntFlag):
    SPAO_NONE = 0
    SPAO_RETAIN_AUDIO = 1


class SpeechRecognizerState(IntFlag):
    SRSInactive = 0
    SRSActive = 1
    SRSActiveAlways = 2
    SRSInactiveWithPurge = 3


class SPSEMANTICFORMAT(IntFlag):
    SPSMF_SAPI_PROPERTIES = 0
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS = 1
    SPSMF_SRGS_SAPIPROPERTIES = 2
    SPSMF_UPS = 4
    SPSMF_SRGS_SEMANTICINTERPRETATION_W3C = 8


class SPBOOKMARKOPTIONS(IntFlag):
    SPBO_NONE = 0
    SPBO_PAUSE = 1
    SPBO_AHEAD = 2
    SPBO_TIME_UNITS = 4


class SPCONTEXTSTATE(IntFlag):
    SPCS_DISABLED = 0
    SPCS_ENABLED = 1


class SPADAPTATIONRELEVANCE(IntFlag):
    SPAR_Unknown = 0
    SPAR_Low = 1
    SPAR_Medium = 2
    SPAR_High = 3


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


class SPCATEGORYTYPE(IntFlag):
    SPCT_COMMAND = 0
    SPCT_DICTATION = 1
    SPCT_SLEEP = 2
    SPCT_SUB_COMMAND = 3
    SPCT_SUB_DICTATION = 4


class SpeechInterference(IntFlag):
    SINone = 0
    SINoise = 1
    SINoSignal = 2
    SITooLoud = 3
    SITooQuiet = 4
    SITooFast = 5
    SITooSlow = 6


class SpeechSpecialTransitionType(IntFlag):
    SSTTWildcard = 1
    SSTTDictation = 2
    SSTTTextBuffer = 3


class DISPID_SpeechWaveFormatEx(IntFlag):
    DISPID_SWFEFormatTag = 1
    DISPID_SWFEChannels = 2
    DISPID_SWFESamplesPerSec = 3
    DISPID_SWFEAvgBytesPerSec = 4
    DISPID_SWFEBlockAlign = 5
    DISPID_SWFEBitsPerSample = 6
    DISPID_SWFEExtraData = 7


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


class DISPID_SpeechMemoryStream(IntFlag):
    DISPID_SMSSetData = 100
    DISPID_SMSGetData = 101


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


class DISPID_SpeechAudioBufferInfo(IntFlag):
    DISPID_SABIMinNotification = 1
    DISPID_SABIBufferSize = 2
    DISPID_SABIEventBias = 3


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


class SpeechEmulationCompareFlags(IntFlag):
    SECFIgnoreCase = 1
    SECFIgnoreKanaType = 65536
    SECFIgnoreWidth = 131072
    SECFNoSpecialChars = 536870912
    SECFEmulateResult = 1073741824
    SECFDefault = 196609


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


class DISPID_SpeechAudio(IntFlag):
    DISPID_SAStatus = 200
    DISPID_SABufferInfo = 201
    DISPID_SADefaultFormat = 202
    DISPID_SAVolume = 203
    DISPID_SABufferNotifySize = 204
    DISPID_SAEventHandle = 205
    DISPID_SASetState = 206


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


class DISPID_SpeechMMSysAudio(IntFlag):
    DISPID_SMSADeviceId = 300
    DISPID_SMSALineId = 301
    DISPID_SMSAMMHandle = 302


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


class DISPID_SpeechAudioStatus(IntFlag):
    DISPID_SASFreeBufferSpace = 1
    DISPID_SASNonBlockingIO = 2
    DISPID_SASState = 3
    DISPID_SASCurrentSeekPosition = 4
    DISPID_SASCurrentDevicePosition = 5


class DISPID_SpeechCustomStream(IntFlag):
    DISPID_SCSBaseStream = 100


class DISPID_SpeechBaseStream(IntFlag):
    DISPID_SBSFormat = 1
    DISPID_SBSRead = 2
    DISPID_SBSWrite = 3
    DISPID_SBSSeek = 4


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


class DISPID_SpeechGrammarRuleStateTransitions(IntFlag):
    DISPID_SGRSTsCount = 1
    DISPID_SGRSTsItem = 0
    DISPID_SGRSTs_NewEnum = -4


class DISPID_SpeechGrammarRule(IntFlag):
    DISPID_SGRAttributes = 1
    DISPID_SGRInitialState = 2
    DISPID_SGRName = 3
    DISPID_SGRId = 4
    DISPID_SGRClear = 5
    DISPID_SGRAddResource = 6
    DISPID_SGRAddState = 7


class SpeechStreamSeekPositionType(IntFlag):
    SSSPTRelativeToStart = 0
    SSSPTRelativeToCurrentPosition = 1
    SSSPTRelativeToEnd = 2


class SPWORDTYPE(IntFlag):
    eWORDTYPE_ADDED = 1
    eWORDTYPE_DELETED = 2


class SpeechDataKeyLocation(IntFlag):
    SDKLDefaultLocation = 0
    SDKLCurrentUser = 1
    SDKLLocalMachine = 2
    SDKLCurrentConfig = 5


class DISPID_SpeechRecognizerStatus(IntFlag):
    DISPID_SRSAudioStatus = 1
    DISPID_SRSCurrentStreamPosition = 2
    DISPID_SRSCurrentStreamNumber = 3
    DISPID_SRSNumberOfActiveRules = 4
    DISPID_SRSClsidEngine = 5
    DISPID_SRSSupportedLanguages = 6


class SPSHORTCUTTYPE(IntFlag):
    SPSHT_NotOverriden = -1
    SPSHT_Unknown = 0
    SPSHT_EMAIL = 4096
    SPSHT_OTHER = 8192
    SPPS_RESERVED1 = 12288
    SPPS_RESERVED2 = 16384
    SPPS_RESERVED3 = 20480
    SPPS_RESERVED4 = 61440


class DISPID_SpeechGrammarRuleStateTransition(IntFlag):
    DISPID_SGRSTType = 1
    DISPID_SGRSTText = 2
    DISPID_SGRSTRule = 3
    DISPID_SGRSTWeight = 4
    DISPID_SGRSTPropertyName = 5
    DISPID_SGRSTPropertyId = 6
    DISPID_SGRSTPropertyValue = 7
    DISPID_SGRSTNextState = 8


class DISPID_SpeechGrammarRuleState(IntFlag):
    DISPID_SGRSRule = 1
    DISPID_SGRSTransitions = 2
    DISPID_SGRSAddWordTransition = 3
    DISPID_SGRSAddRuleTransition = 4
    DISPID_SGRSAddSpecialTransition = 5


class SpeechGrammarState(IntFlag):
    SGSEnabled = 1
    SGSDisabled = 0
    SGSExclusive = 3


class SpeechLoadOption(IntFlag):
    SLOStatic = 0
    SLODynamic = 1


class SpeechRuleState(IntFlag):
    SGDSInactive = 0
    SGDSActive = 1
    SGDSActiveWithAutoPause = 3
    SGDSActiveUserDelimited = 4


class SpeechWordPronounceable(IntFlag):
    SWPUnknownWordUnpronounceable = 0
    SWPUnknownWordPronounceable = 1
    SWPKnownWordPronounceable = 2


class DISPID_SpeechGrammarRules(IntFlag):
    DISPID_SGRsCount = 1
    DISPID_SGRsDynamic = 2
    DISPID_SGRsAdd = 3
    DISPID_SGRsCommit = 4
    DISPID_SGRsCommitAndSave = 5
    DISPID_SGRsFindRule = 6
    DISPID_SGRsItem = 0
    DISPID_SGRs_NewEnum = -4


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


class SpeechVisemeFeature(IntFlag):
    SVF_None = 0
    SVF_Stressed = 1
    SVF_Emphasis = 2


class _SPAUDIOSTATE(IntFlag):
    SPAS_CLOSED = 0
    SPAS_STOP = 1
    SPAS_PAUSE = 2
    SPAS_RUN = 3


class SpeechRuleAttributes(IntFlag):
    SRATopLevel = 1
    SRADefaultToActive = 2
    SRAExport = 4
    SRAImport = 8
    SRAInterpreter = 16
    SRADynamic = 32
    SRARoot = 64


class SPWAVEFORMATTYPE(IntFlag):
    SPWF_INPUT = 0
    SPWF_SRENGINE = 1


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


class SpeechFormatType(IntFlag):
    SFTInput = 0
    SFTSREngine = 1


class SPXMLRESULTOPTIONS(IntFlag):
    SPXRO_SML = 0
    SPXRO_Alternates_SML = 1


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


class SpeechRunState(IntFlag):
    SRSEDone = 1
    SRSEIsSpeaking = 2


class DISPID_SpeechRecoResult2(IntFlag):
    DISPID_SRRSetTextFeedback = 12


class DISPID_SpeechPhraseBuilder(IntFlag):
    DISPID_SPPBRestorePhraseFromMemory = 1


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


class DISPID_SpeechPhraseElements(IntFlag):
    DISPID_SPEsCount = 1
    DISPID_SPEsItem = 0
    DISPID_SPEs_NewEnum = -4


class DISPID_SpeechPhraseReplacement(IntFlag):
    DISPID_SPRDisplayAttributes = 1
    DISPID_SPRText = 2
    DISPID_SPRFirstElement = 3
    DISPID_SPRNumberOfElements = 4


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


class SPDATAKEYLOCATION(IntFlag):
    SPDKL_DefaultLocation = 0
    SPDKL_CurrentUser = 1
    SPDKL_LocalMachine = 2
    SPDKL_CurrentConfig = 5


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


class SpeechStreamFileMode(IntFlag):
    SSFMOpenForRead = 0
    SSFMOpenReadWrite = 1
    SSFMCreate = 2
    SSFMCreateForWrite = 3


class SPLOADOPTIONS(IntFlag):
    SPLO_STATIC = 0
    SPLO_DYNAMIC = 1


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


class SpeechGrammarWordType(IntFlag):
    SGDisplay = 0
    SGLexical = 1
    SGPronounciation = 2
    SGLexicalNoSpecialChars = 3


class SpeechAudioState(IntFlag):
    SASClosed = 0
    SASStop = 1
    SASPause = 2
    SASRun = 3


class SpeechWordType(IntFlag):
    SWTAdded = 1
    SWTDeleted = 2


class SPFILEMODE(IntFlag):
    SPFM_OPEN_READONLY = 0
    SPFM_OPEN_READWRITE = 1
    SPFM_CREATE = 2
    SPFM_CREATE_ALWAYS = 3
    SPFM_NUM_MODES = 4


class SpeechDisplayAttributes(IntFlag):
    SDA_No_Trailing_Space = 0
    SDA_One_Trailing_Space = 2
    SDA_Two_Trailing_Spaces = 4
    SDA_Consume_Leading_Spaces = 8


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


class SPRECOSTATE(IntFlag):
    SPRST_INACTIVE = 0
    SPRST_ACTIVE = 1
    SPRST_ACTIVE_ALWAYS = 2
    SPRST_INACTIVE_WITH_PURGE = 3
    SPRST_NUM_STATES = 4


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


class SpeechGrammarRuleStateTransitionType(IntFlag):
    SGRSTTEpsilon = 0
    SGRSTTWord = 1
    SGRSTTRule = 2
    SGRSTTDictation = 3
    SGRSTTWildcard = 4
    SGRSTTTextBuffer = 5


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


class SpeechRetainedAudioOptions(IntFlag):
    SRAONone = 0
    SRAORetainAudio = 1


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


class DISPID_SpeechObjectTokens(IntFlag):
    DISPID_SOTsCount = 1
    DISPID_SOTsItem = 0
    DISPID_SOTs_NewEnum = -4


class SPRULESTATE(IntFlag):
    SPRS_INACTIVE = 0
    SPRS_ACTIVE = 1
    SPRS_ACTIVE_WITH_AUTO_PAUSE = 3
    SPRS_ACTIVE_USER_DELIMITED = 4


SPAUDIOSTATE = _SPAUDIOSTATE
SPSTREAMFORMATTYPE = SPWAVEFORMATTYPE


__all__ = [
    'SPGS_ENABLED', 'DISPID_SPRules_NewEnum', 'SpMMAudioEnum',
    'WAVEFORMATEX', 'DISPID_SPIEngineId',
    'DISPID_SpeechGrammarRuleStateTransitions', 'ISpeechRecoContext',
    'SREStateChange', 'SREFalseRecognition', 'DISPID_SGRSTNextState',
    'DISPID_SVEventInterests', 'SLOStatic',
    '_ISpeechRecoContextEvents', 'SREBookmark', 'DISPID_SLWs_NewEnum',
    'SpeechEmulationCompareFlags', 'SRADefaultToActive', 'SPBO_NONE',
    'DISPID_SPILanguageId', 'SPEI_FALSE_RECOGNITION',
    'SAFT16kHz8BitMono', 'SRCS_Disabled', 'SASPause',
    'ISpeechPhraseRules', 'ISpNotifyTranslator',
    'SpeechAddRemoveWord', 'ISpeechPhraseElements', 'SPSVerb',
    'DISPID_SpeechLexicon', 'DISPID_SPRulesCount',
    'SDA_Consume_Leading_Spaces', 'DISPID_SOTGetStorageFileName',
    'SPSMF_SRGS_SAPIPROPERTIES', 'DISPID_SVWaitUntilDone',
    'SGRSTTDictation', 'SPINTERFERENCE_LATENCY_WARNING',
    'SpeechTokenShellFolder', 'DISPID_SRGetPropertyString',
    'DISPID_SGRsDynamic', 'ISpEventSink', 'DISPID_SRCERecognition',
    'SGRSTTEpsilon', 'SRSEIsSpeaking', 'DISPID_SLWsCount',
    'SpeechTokenKeyAttributes', 'DISPID_SWFESamplesPerSec',
    'SPEI_RECO_OTHER_CONTEXT', 'DISPID_SVSVisemeId',
    'DISPID_SpeechRecognizer', 'DISPID_SAStatus',
    'DISPID_SPPEngineConfidence', 'DISPID_SVSInputWordPosition',
    'DISPID_SOTSetId', '__MIDL___MIDL_itf_sapi_0000_0020_0002',
    'ISpRecoResult', 'DISPID_SPEActualConfidence', 'SPFILEMODE',
    'tagSPTEXTSELECTIONINFO', 'SAFT32kHz8BitMono',
    'DISPID_SDKSetLongValue', 'SPFM_CREATE_ALWAYS',
    'DISPID_SAFGetWaveFormatEx', 'SpLexicon', 'ISpeechPhraseProperty',
    'SAFT22kHz16BitStereo', 'SPEI_REQUEST_UI',
    'DISPID_SGRInitialState', 'SPEI_MAX_SR',
    'DISPID_SPIAudioSizeBytes', 'SPPHRASEREPLACEMENT', 'SITooSlow',
    'SPWP_KNOWN_WORD_PRONOUNCEABLE', 'DISPIDSPTSI',
    'DISPID_SDKOpenKey', 'SAFTCCITT_ALaw_11kHzStereo',
    'Speech_StreamPos_Asap', 'SpNotifyTranslator',
    'DISPID_SOTDataKey', 'SPAUDIOSTATUS', 'DISPID_SRGIsPronounceable',
    'DISPID_SpeechPhraseProperty', 'SAFTCCITT_ALaw_44kHzStereo',
    'SpeechEngineProperties', 'DISPID_SGRSTsCount', 'SPEI_RESERVED6',
    'DISPID_SPIGetDisplayAttributes', 'SGRSTTWord', 'SRTReSent',
    'SVP_0', 'SWPKnownWordPronounceable', 'eLEXTYPE_PRIVATE7',
    'DISPID_SGRsCommit', 'DISPID_SPPId',
    'SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE', 'SPEI_VOICE_CHANGE',
    'SPDKL_CurrentUser', 'eWORDTYPE_ADDED', 'SVEStartInputStream',
    'SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN', 'SpeechAudioState',
    'DISPID_SPIEnginePrivateData', 'DISPID_SpeechGrammarRules',
    'DISPID_SRDisplayUI', 'IStream', 'SVP_13', 'SVSFIsNotXML',
    'SPPS_RESERVED1', 'ISpResourceManager', 'SECFIgnoreKanaType',
    'DISPID_SABIBufferSize', 'DISPID_SPERetainedSizeBytes',
    'SPEVENTENUM', 'DISPID_SRGRecoContext', 'SDKLDefaultLocation',
    'SpeechWordType', 'eLEXTYPE_USER_SHORTCUT', 'SREPhraseStart',
    'SAFTCCITT_ALaw_22kHzMono', 'SPAR_Low', 'DISPID_SCSBaseStream',
    'SDTReplacement', 'DISPID_SRSCurrentStreamPosition', 'SDTAudio',
    'SDKLCurrentUser', 'SPLOADOPTIONS', 'SVF_None',
    'DISPID_SDKSetBinaryValue', 'SINoise', 'ISpNotifySource',
    'SPEI_RESERVED2', 'SPLO_STATIC', 'DISPID_SRRTLength',
    'DISPID_SPRuleChildren', 'IInternetSecurityManager',
    'DISPID_SPACommit', 'SpVoice', 'DISPID_SRIsUISupported',
    'SGRSTTRule', 'DISPID_SpeechPhraseElements', 'DISPID_SPPValue',
    'SGRSTTTextBuffer', 'DISPID_SPISaveToMemory',
    'ISpeechCustomStream', 'SREStreamEnd',
    'DISPID_SpeechPhraseProperties', 'SPEI_SR_PRIVATE',
    'SAFT12kHz16BitMono',
    'DISPID_SRAllowVoiceFormatMatchingOnNextSet',
    'DISPID_SDKGetBinaryValue', 'SPDKL_DefaultLocation',
    'ISpeechPhraseReplacement', 'SVP_3', 'ISpeechGrammarRuleState',
    'SPPROPERTYINFO', 'DISPID_SpeechPhraseBuilder', 'SVP_9',
    'SAFTCCITT_uLaw_11kHzStereo', 'DISPID_SRCRetainedAudioFormat',
    'SpSharedRecoContext', 'SRTStandard', 'SPFM_OPEN_READWRITE',
    'SECNormalConfidence', 'SP_VISEME_13', '_RemotableHandle',
    'SPRECOGNIZERSTATUS', 'DISPID_SRRSpeakAudio',
    'DISPID_SVSyncronousSpeakTimeout', 'ISpeechLexiconWord',
    'DISPID_SPPName', 'DISPID_SVSpeakCompleteEvent', 'SPCT_COMMAND',
    'ISpLexicon', 'DISPID_SLPsCount', 'SVP_7', 'SPEI_TTS_AUDIO_LEVEL',
    'DISPID_SpeechDataKey', 'SPFM_OPEN_READONLY', 'SPSNoun',
    'SVSFPersistXML', 'SPWT_DISPLAY', 'SREStreamStart',
    'SpeechGrammarTagWildcard', 'ISpeechTextSelectionInformation',
    'DISPID_SRSSupportedLanguages', 'ISpeechRecoResult',
    'SAFTCCITT_ALaw_11kHzMono', 'SpeechRecognizerState',
    'SpeechVoiceCategoryTTSRate', 'DISPID_SpeechLexiconProns',
    'DISPID_SVGetVoices', 'DISPID_SRGCommit',
    'DISPID_SPRuleNumberOfElements', 'SpeechRecoProfileProperties',
    'DISPID_SpeechPhraseElement', 'SDTAlternates', 'SP_VISEME_18',
    'DISPID_SPIRetainedSizeBytes', 'eLEXTYPE_PRIVATE19',
    'DISPID_SGRSAddWordTransition', 'DISPID_SVSInputSentenceLength',
    'SPEI_HYPOTHESIS', 'SVP_20', 'SpFileStream', 'SREHypothesis',
    'DISPID_SRCEPhraseStart', 'DISPID_SLPLangId', 'SPPS_Unknown',
    'SAFTGSM610_44kHzMono', 'DISPID_SRGCmdLoadFromObject',
    'DISPID_SPRuleEngineConfidence', 'SpeechVoiceSpeakFlags',
    'DISPID_SpeechLexiconWord', 'SPTEXTSELECTIONINFO', 'SPBO_PAUSE',
    'SPWORD', 'DISPID_SGRsAdd', 'DISPID_SOTCDefault',
    'SVSFNLPSpeakPunc', 'ISpDataKey',
    'DISPID_SpeechGrammarRuleStateTransition',
    'DISPID_SVGetAudioOutputs', 'DISPID_SRRPhraseInfo',
    'SAFT12kHz8BitStereo', 'DISPID_SRGDictationUnload',
    'SSSPTRelativeToStart', 'SpeechTokenValueCLSID',
    'SPDKL_CurrentConfig', 'SPEI_SOUND_END', 'SAFT32kHz16BitMono',
    'SAFTNonStandardFormat', 'SRARoot', 'DISPID_SRRAudioFormat',
    'DISPID_SPCPhoneToId', 'SVF_Emphasis', 'SPPS_Function',
    'SRESoundStart', 'SPSMF_UPS', 'DISPID_SRCERecognizerStateChange',
    'DISPID_SPEAudioStreamOffset', 'SVPNormal',
    'DISPID_SLWPronunciations', 'SPSEMANTICERRORINFO', 'SP_VISEME_19',
    'SpeechPartOfSpeech', 'SPSHORTCUTTYPE',
    'DISPID_SRGetPropertyNumber', 'DISPID_SBSWrite', 'SGSExclusive',
    'DISPID_SpeechRecoContextEvents', 'SPSHT_NotOverriden',
    'SPAR_High', 'SECFNoSpecialChars', 'SAFTADPCM_8kHzStereo',
    'DISPID_SVEEnginePrivate', 'SSFMCreateForWrite',
    'eLEXTYPE_PRIVATE20', 'SPCS_DISABLED', 'SPSTREAMFORMATTYPE',
    'DISPID_SABufferInfo', 'SP_VISEME_3', 'SpeechTokenContext',
    'SAFTADPCM_22kHzMono', 'DISPID_SpeechPhraseAlternates',
    'DISPID_SVPause', 'SECFIgnoreCase', 'SVPOver', 'DISPID_SPPsItem',
    'SVEBookmark', 'SVSFIsFilename', 'DISPID_SMSADeviceId',
    'SREAudioLevel', '_SPAUDIOSTATE', 'DISPID_SAVolume',
    'DISPID_SRRTTickCount', 'DISPID_SRGCmdLoadFromMemory',
    'SPEI_TTS_BOOKMARK', 'typelib_path', 'SRAImport',
    'SPWORDPRONUNCIATION', 'SPPS_SuppressWord', 'SPCS_ENABLED',
    'SRTAutopause', 'SPEI_VISEME', 'SVP_19', 'ISpeechMemoryStream',
    'SPDATAKEYLOCATION', 'ISpeechGrammarRules', 'SPGRAMMARSTATE',
    'SPLEXICONTYPE', 'SDA_One_Trailing_Space', 'DISPID_SWFEExtraData',
    'DISPID_SGRSTs_NewEnum', 'DISPID_SGRSRule', 'DISPID_SRGetFormat',
    'DISPID_SVSInputSentencePosition', 'SPAR_Medium', 'SVP_17',
    'SPEI_END_SR_STREAM', 'SpeechDictationTopicSpelling',
    'SpObjectToken', 'SpeechAudioVolume', 'SpeechUserTraining',
    'DISPID_SVESentenceBoundary', 'DISPID_SPRuleParent',
    'DISPID_SVSLastResult', 'ISpObjectTokenCategory',
    'eLEXTYPE_PRIVATE16', 'SRERequestUI', 'DISPID_SVVolume',
    'SAFT11kHz16BitStereo', 'ISpeechAudioFormat',
    'SAFT44kHz16BitMono', 'DISPIDSPRG', 'SAFT32kHz16BitStereo',
    'SAFT48kHz16BitStereo', 'ISpeechObjectToken', 'SVEVoiceChange',
    'DISPID_SVAllowAudioOuputFormatChangesOnNextSet',
    'DISPID_SASetState', 'SpeechRuleAttributes', 'DISPID_SMSALineId',
    'SRSInactiveWithPurge', 'DISPID_SPEsCount', 'ISpeechRecoResult2',
    'SPINTERFERENCE_TOOSLOW', 'SP_VISEME_6', 'DISPID_SRCEBookmark',
    'DISPID_SRCEPropertyStringChange', 'ISpeechPhraseAlternate',
    'SPVPRI_ALERT', 'DISPID_SpeechRecoContext', 'SPSHORTCUTPAIRLIST',
    'SECLowConfidence', 'ISpeechDataKey', 'DISPID_SRGState',
    'DISPID_SpeechPhraseAlternate', 'SP_VISEME_9', 'SP_VISEME_4',
    'DISPID_SMSGetData', 'DISPID_SRCVoicePurgeEvent',
    'DISPID_SRCEAdaptation', 'SPSModifier', 'ISpeechPhraseAlternates',
    'SASClosed', 'DISPID_SWFEBlockAlign', 'SDTLexicalForm',
    'SPAUDIOBUFFERINFO', 'SVEAudioLevel', 'DISPID_SLPsItem',
    'SP_VISEME_17', 'SPEI_SR_AUDIO_LEVEL', 'SPEI_SOUND_START',
    'DISPID_SOTsCount', 'DISPID_SVSLastStreamNumberQueued',
    'DISPID_SPIElements', 'SSFMCreate', 'DISPID_SAFSetWaveFormatEx',
    'SpMMAudioIn', 'IEnumSpObjectTokens', 'Speech_Default_Weight',
    'DISPID_SPEDisplayText', 'DISPID_SPRuleName', 'SRADynamic',
    'DISPID_SGRId', 'SGSEnabled', 'SpStream', 'SRERecognition',
    'DISPID_SOTGetDescription', 'SVSFPurgeBeforeSpeak',
    'DISPID_SOTs_NewEnum', 'SAFT11kHz8BitMono', 'ISpStreamFormat',
    'DISPIDSPTSI_SelectionOffset', 'DISPID_SWFEFormatTag',
    'DISPID_SpeechMemoryStream', 'SITooQuiet', 'SVSFParseSapi',
    'DISPID_SBSRead', 'ISpRecognizer3', 'SpeechAudioProperties',
    'SAFTADPCM_44kHzStereo', 'DISPID_SRGSetWordSequenceData',
    'SAFTCCITT_ALaw_44kHzMono', 'SpeechWordPronounceable',
    'DISPID_SpeechPhraseInfo', 'DISPID_SDKEnumKeys', 'SRATopLevel',
    'SFTInput', 'SpPhoneticAlphabetConverter', 'SAFT16kHz16BitStereo',
    'ISpeechLexiconPronunciation', 'SPRECOSTATE',
    'SpeechVoiceSkipTypeSentence', 'DISPID_SpeechObjectTokens',
    '__MIDL_IWinTypes_0009', 'SREPropertyStringChange',
    'SAFT11kHz16BitMono', 'DISPID_SRCreateRecoContext',
    'DISPID_SGRSTText', 'DISPID_SOTIsUISupported', 'SPRS_ACTIVE',
    'eLEXTYPE_RESERVED6', 'SPEI_MIN_TTS',
    'SpTextSelectionInformation', 'SGSDisabled', 'SPWF_INPUT',
    'SPSERIALIZEDPHRASE', 'DISPID_SGRSTransitions',
    'DISPID_SOTMatchesAttributes', 'SpPhraseInfoBuilder',
    'SRAORetainAudio', 'eLEXTYPE_RESERVED4', 'SPWF_SRENGINE',
    'SPSHT_OTHER', 'SPVOICESTATUS', 'DISPID_SRCSetAdaptationData',
    'DISPID_SOTsItem', 'DISPID_SRCEEnginePrivate',
    'SpeechVoiceEvents', 'DISPID_SGRSTPropertyName',
    'ISpeechRecognizer', 'SAFTNoAssignedFormat', 'ISpRecognizer2',
    'DISPID_SVEVoiceChange', 'DISPID_SRCState', 'DISPID_SRCBookmark',
    'SAFT22kHz8BitMono', 'DISPID_SABufferNotifySize',
    'DISPID_SVEStreamStart', 'DISPID_SPPsCount', 'SPEVENTSOURCEINFO',
    'eLEXTYPE_PRIVATE8', 'SPEI_UNDEFINED', 'STCLocalServer',
    'SPPS_LMA', 'DISPID_SPAs_NewEnum', 'SpeechTokenIdUserLexicon',
    'SVP_2', 'DISPID_SpeechRecoResultTimes',
    'SAFTCCITT_uLaw_11kHzMono', 'DISPID_SFSClose',
    'ISpeechRecoGrammar', 'SLTApp', 'ISpeechPhraseInfoBuilder',
    'ISpRecoGrammar', 'SGDSActive', 'eLEXTYPE_PRIVATE1',
    'DISPID_SGRs_NewEnum', 'SPPARTOFSPEECH', 'DISPID_SPAPhraseInfo',
    'SPSMF_SRGS_SEMANTICINTERPRETATION_MS',
    'DISPID_SRCEventInterests', 'SpeechRegistryUserRoot',
    'ISpeechGrammarRuleStateTransition', 'LONG_PTR', 'SVP_18',
    'DISPID_SPAsItem', 'SpeechGrammarTagDictation', 'SREPrivate',
    'DISPID_SLRemovePronunciationByPhoneIds', 'DISPID_SDKEnumValues',
    'SpeechVisemeType', 'ISpeechAudioBufferInfo', 'SLODynamic',
    'SVP_1', 'ISpGrammarBuilder', 'SGDSActiveWithAutoPause',
    'DISPID_SPIProperties', 'DISPID_SRCRequestedUIType',
    'SpeechCategoryRecoProfiles', 'SPEI_START_INPUT_STREAM',
    'SpAudioFormat', 'SVSFVoiceMask', 'SRTEmulated', 'SPEVENT',
    'SPGS_DISABLED', 'DISPID_SPRuleId', 'eLEXTYPE_LETTERTOSOUND',
    'SVSFUnusedFlags', 'DISPID_SOTCreateInstance', 'SP_VISEME_7',
    'SGDSActiveUserDelimited', 'DISPID_SLWWord', 'SWTAdded',
    'DISPID_SOTGetAttribute', 'DISPID_SVEWord',
    'DISPID_SpeechAudioFormat', 'DISPID_SPRDisplayAttributes',
    'ISpeechLexiconPronunciations', 'SpeechCategoryAudioIn',
    'ISpSerializeState', 'DISPID_SVSRunningState',
    'DISPID_SMSSetData', 'SECFDefault', 'SVSFlagsAsync', 'SRAONone',
    'SPEI_PROPERTY_STRING_CHANGE', 'DISPID_SOTCEnumerateTokens',
    'SREPropertyNumChange', 'SPAUDIOSTATE', 'SVP_12',
    'DISPID_SGRName', 'eLEXTYPE_PRIVATE6',
    'SpeechAudioFormatGUIDWave', 'SVP_16',
    'DISPID_SPRNumberOfElements', 'ISpPhoneConverter', 'SPPS_Verb',
    'ISpRecoGrammar2', 'SpeechStreamSeekPositionType',
    'ISpeechRecognizerStatus', 'SPSHT_Unknown',
    'DISPID_SRGDictationSetState', 'DISPID_SRCRecognizer',
    'ISpeechLexiconWords', 'STCInprocServer', 'DISPID_SLGenerationId',
    'DISPID_SpeechRecoResult', 'SpeechTokenKeyFiles',
    'SpeechGrammarTagUnlimitedDictation', 'SPWORDPRONOUNCEABLE',
    'DISPID_SABIMinNotification', 'DISPID_SRRTStreamTime',
    'SAFT44kHz8BitMono', 'SVP_6', 'SPBOOKMARKOPTIONS',
    'DISPID_SWFEAvgBytesPerSec', 'SpeechInterference',
    'DISPID_SRGSetTextSelection', 'DISPID_SVIsUISupported',
    'SAFTCCITT_uLaw_44kHzMono', 'DISPID_SOTDisplayUI',
    'SAFT8kHz8BitMono', 'DISPID_SRGReset', 'SRTExtendableParse',
    'DISPID_SAEventHandle', 'SAFTADPCM_11kHzMono', 'SVP_8',
    'SP_VISEME_5', 'SPEI_RECOGNITION', 'DISPID_SRCCmdMaxAlternates',
    'SAFT8kHz16BitMono', 'SpeechDiscardType',
    'DISPID_SPERetainedStreamOffset', 'DISPID_SVEViseme',
    'ISpeechBaseStream', 'DISPID_SVEBookmark',
    'DISPID_SLAddPronunciationByPhoneIds', 'DISPID_SRCCreateGrammar',
    'SVP_21', 'SRSActiveAlways', 'SAFTGSM610_8kHzMono',
    'DISPID_SGRClear', 'SAFTADPCM_22kHzStereo',
    'DISPID_SRRRecoContext', 'SPRST_INACTIVE',
    'DISPID_SASNonBlockingIO', 'SPPHRASEPROPERTY', 'SPPS_RESERVED4',
    'DISPID_SGRSTType', 'SpeechPropertyHighConfidenceThreshold',
    'ISpeechMMSysAudio', 'ISpeechPhraseReplacements', 'DISPID_SOTCId',
    'DISPID_SpeechLexiconWords', 'SASStop', 'eLEXTYPE_PRIVATE4',
    'DISPID_SRGDictationLoad', 'SREAdaptation', 'DISPID_SPAsCount',
    'SpSharedRecognizer', 'eLEXTYPE_PRIVATE9', 'SAFT48kHz8BitMono',
    'DISPID_SREmulateRecognition', 'SECHighConfidence',
    'DISPID_SPRFirstElement', 'DISPID_SGRSTsItem', 'SPPHRASE',
    'DISPID_SLRemovePronunciation', 'SPAUDIOOPTIONS',
    'SGPronounciation', 'DISPID_SPRsCount', 'DISPID_SPPChildren',
    'SPVPRI_NORMAL', 'SPINTERFERENCE_TOOQUIET',
    'ISpeechPhoneConverter', 'SPEI_SR_BOOKMARK', 'SpPhoneConverter',
    'SPDKL_LocalMachine', 'DISPID_SRCEStartStream', 'SVSFParseMask',
    'SpCustomStream', 'ISpeechLexicon', 'SPAS_PAUSE',
    'DISPID_SVEAudioLevel', 'DISPID_SGRAttributes',
    'SDA_No_Trailing_Space', 'tagSPPROPERTYINFO',
    'SpInProcRecoContext', 'SECFEmulateResult', 'ISpProperties',
    'DISPIDSPTSI_SelectionLength', 'SPCT_SLEEP', 'DISPID_SVRate',
    'SPCT_SUB_COMMAND', 'ISpAudio', 'SAFT48kHz8BitStereo',
    'DISPID_SGRsCount', 'DISPID_SABIEventBias', 'DISPID_SPPParent',
    'SpeechTokenKeyUI', 'SPEI_RESERVED3', 'SPPS_Interjection',
    'SpeechRecognitionType', 'SPSMF_SRGS_SEMANTICINTERPRETATION_W3C',
    'SAFTCCITT_uLaw_8kHzMono', 'SPRECOCONTEXTSTATUS',
    'SPRS_ACTIVE_WITH_AUTO_PAUSE', 'SASRun', 'DISPID_SPIGrammarId',
    'ISpeechPhraseRule', 'SDTPronunciation', 'DISPID_SpeechAudio',
    'SAFTCCITT_ALaw_8kHzMono', 'DISPID_SRGCmdLoadFromFile',
    'SFTSREngine', 'DISPID_SpeechRecoResult2', 'SPGS_EXCLUSIVE',
    'DISPID_SPRuleFirstElement', 'eLEXTYPE_PRIVATE18',
    'DISPID_SGRsCommitAndSave', 'SPEI_RESERVED5', 'SDKLCurrentConfig',
    'SAFT16kHz16BitMono', 'SpeechCategoryRecognizers', 'SP_VISEME_14',
    'DISPID_SVPriority', 'SpeechGrammarRuleStateTransitionType',
    'DISPID_SRState', 'DISPID_SRSClsidEngine',
    'DISPID_SRCEFalseRecognition', 'ISpeechPhraseElement',
    'SRAInterpreter', 'ISpeechAudioStatus', 'SAFT48kHz16BitMono',
    'ISpPhoneticAlphabetConverter', 'SAFTCCITT_ALaw_8kHzStereo',
    'SpeechCategoryVoices', 'DISPID_SVGetProfiles',
    'SPWT_LEXICAL_NO_SPECIAL_CHARS', 'SBONone', 'IEnumString',
    'STSF_AppData', 'SPINTERFERENCE_TOOLOUD',
    'DISPID_SDKGetlongValue', 'DISPID_SBSFormat',
    'DISPID_SRSCurrentStreamNumber', 'SpeechLexiconType',
    'ISpeechXMLRecoResult', 'SPEI_WORD_BOUNDARY',
    '_ISpeechVoiceEvents', 'DISPID_SRCCreateResultFromMemory',
    'DISPID_SLWLangId', 'DISPID_SOTCategory', 'DISPID_SLPSymbolic',
    'DISPID_SASCurrentDevicePosition', 'ISpeechRecoResultTimes',
    'SGDisplay', 'DISPID_SVSInputWordLength', 'SpeechStreamFileMode',
    'SPSERIALIZEDRESULT', 'SpeechPropertyAdaptationOn', 'SPEI_MIN_SR',
    'SPPS_NotOverriden', 'DISPID_SpeechRecognizerStatus',
    'SAFT16kHz8BitStereo', 'DISPID_SWFEChannels', 'SPINTERFERENCE',
    'SpeechAllElements', 'SPPS_Noun', 'SPVISEMES',
    'DISPID_SRSNumberOfActiveRules', 'SpeechRecoEvents',
    'DISPID_SPEAudioSizeBytes', 'DISPID_SpeechPhraseReplacements',
    'DISPID_SPCIdToPhone', 'SpeechPropertyResourceUsage',
    'SPWORDLIST', 'STCRemoteServer', 'SVSFNLPMask',
    'SPWP_UNKNOWN_WORD_PRONOUNCEABLE',
    'DISPID_SPIAudioStreamPosition', 'SPSHORTCUTPAIR',
    'DISPID_SPPConfidence', 'SP_VISEME_11', 'SpObjectTokenCategory',
    'SpeechAudioFormatGUIDText', 'Speech_Max_Word_Length',
    'DISPID_SVAlertBoundary', 'DISPID_SRRTimes',
    'SPEI_SR_RETAINEDAUDIO', 'DISPID_SGRSTPropertyId',
    'SPINTERFERENCE_NOSIGNAL', 'SPPHRASEELEMENT', 'SINoSignal',
    'SP_VISEME_10', 'STSF_LocalAppData', 'DISPID_SDKDeleteValue',
    'DISPID_SVSPhonemeId', 'DISPID_SLGetGenerationChange',
    'SPEI_END_INPUT_STREAM', 'DISPID_SRSetPropertyString',
    'DISPID_SpeechAudioStatus', 'SAFTDefault', 'eLEXTYPE_APP',
    'DISPID_SRStatus', 'SpStreamFormatConverter',
    'DISPID_SRCRetainedAudio', 'SPFM_CREATE', 'DISPID_SGRsItem',
    'DISPID_SLGetPronunciations', 'DISPID_SpeechVoiceStatus',
    'SPRST_ACTIVE', 'SPEI_PHRASE_START', 'SPXRO_Alternates_SML',
    'SPFM_NUM_MODES', 'DISPID_SVAudioOutputStream',
    'DISPID_SRCESoundStart', 'DISPID_SPIGetText', 'STSF_FlagCreate',
    'DISPID_SOTRemove', 'SP_VISEME_16', 'SPWORDTYPE',
    'DISPID_SpeechAudioBufferInfo', 'ISpStreamFormatConverter',
    'SpeechVoicePriority', 'ISpPhoneticAlphabetSelection',
    'SAFT12kHz8BitMono', 'DISPID_SOTCSetId', 'DISPID_SPCLangId',
    'SPSHT_EMAIL', 'DISPID_SLWsItem', 'DISPID_SRCEHypothesis',
    'SPRST_NUM_STATES', 'SPEI_MAX_TTS', 'eLEXTYPE_MORPHOLOGY',
    'SGRSTTWildcard', 'SPAO_RETAIN_AUDIO', 'SpMemoryStream', 'SVP_14',
    'DISPID_SpeechPhraseRules', 'SP_VISEME_20', 'SPPS_Modifier',
    'SDKLLocalMachine', 'DISPID_SDKGetStringValue',
    'DISPID_SpeechObjectToken', 'SAFTText', 'SP_VISEME_21',
    'SpeechLoadOption', 'SWTDeleted', 'DISPID_SRCEEndStream',
    'DISPID_SVSLastBookmarkId', 'DISPID_SFSOpen',
    'DISPID_SVEStreamEnd', 'SPRST_ACTIVE_ALWAYS', 'SRSActive',
    'SAFT24kHz16BitMono', 'ISpObjectWithToken', 'ISpRecoContext',
    'SAFT8kHz8BitStereo', 'ISpXMLRecoResult', 'SPEI_RESERVED1',
    'SVP_11', 'SpUnCompressedLexicon', 'DISPID_SPEDisplayAttributes',
    'DISPID_SpeechFileStream', 'eLEXTYPE_PRIVATE14',
    'SpeechDataKeyLocation', 'DISPID_SAFType', 'SPINTERFERENCE_NONE',
    'SPEI_START_SR_STREAM', 'SWPUnknownWordPronounceable',
    'SPINTERFERENCE_TOOFAST', 'SVSFParseSsml',
    'DISPID_SRRDiscardResultInfo',
    'DISPID_SRCERecognitionForOtherContext', 'SRERecoOtherContext',
    'SAFT24kHz8BitMono', 'SpInprocRecognizer', 'DISPID_SGRsFindRule',
    'DISPID_SRRSaveToMemory', 'SVSFParseAutodetect',
    'DISPID_SPPNumberOfElements', 'SpeechGrammarState',
    'DISPID_SRGCmdLoadFromProprietaryGrammar', 'SPLO_DYNAMIC',
    'DISPID_SRSetPropertyNumber', 'DISPID_SGRSAddSpecialTransition',
    'DISPID_SWFEBitsPerSample', 'ISpeechPhraseProperties',
    'DISPID_SRRTOffsetFromStart', 'SAFT22kHz8BitStereo',
    'DISPID_SLPPhoneIds', 'SpeechCategoryAudioOut', 'SVEPrivate',
    'DISPID_SRAudioInput', 'DISPID_SVDisplayUI',
    'eLEXTYPE_RESERVED10', 'DISPID_SRRAudio',
    'DISPID_SLPPartOfSpeech', 'DISPID_SPPBRestorePhraseFromMemory',
    'SpeechRunState', 'SSFMOpenReadWrite', 'SRSEDone',
    'DISPID_SPAStartElementInResult', 'SVEPhoneme',
    'SpeechPropertyNormalConfidenceThreshold', 'DISPID_SVVoice',
    'DISPID_SGRAddState', 'SITooLoud', 'DISPID_SpeechCustomStream',
    'SPCATEGORYTYPE', 'DISPID_SRGCmdSetRuleIdState',
    'DISPID_SPIStartTime', 'SAFTADPCM_44kHzMono',
    'DISPID_SPRs_NewEnum', 'SPVPRIORITY', 'ISpRecoCategory',
    'eLEXTYPE_PRIVATE2', 'DISPID_SGRAddResource',
    'DISPID_SRCERequestUI', 'DISPID_SLAddPronunciation',
    'eLEXTYPE_RESERVED9', 'ISpPhraseAlt', 'Library',
    'DISPID_SPARecoResult', 'SpeechGrammarWordType',
    'SAFT32kHz8BitStereo', 'SpNullPhoneConverter',
    'DISPID_SRCEPropertyNumberChange', 'DISPID_SRCESoundEnd',
    'DISPID_SPIAudioSizeTime', 'DISPID_SLGetWords',
    'ISpeechObjectTokens', 'DISPID_SVResume',
    'SAFTExtendedAudioFormat', 'DISPID_SRProfile',
    'DISPID_SLPs_NewEnum', 'SPEI_ACTIVE_CATEGORY_CHANGED',
    'SPRULESTATE', 'SBOPause', 'SpeechPropertyComplexResponseSpeed',
    'SVSFIsXML', 'eLEXTYPE_PRIVATE3', 'SPSMF_SAPI_PROPERTIES',
    'SpeechVisemeFeature', 'SP_VISEME_12',
    'SPRST_INACTIVE_WITH_PURGE', 'DISPID_SVAudioOutput',
    'DISPID_SRIsShared', 'DISPID_SVStatus', 'SPAS_RUN', 'SVP_5',
    'DISPID_SASState', 'STCAll', 'DISPID_SRRGetXMLResult',
    'SVEAllEvents', 'DISPID_SPRulesItem', 'DISPID_SVGetAudioInputs',
    'SP_VISEME_0', 'SPWT_LEXICAL', 'SSSPTRelativeToCurrentPosition',
    'SPPS_RESERVED2', 'DISPID_SpeechMMSysAudio', 'tagSTATSTG',
    'SpShortcut', 'SSTTDictation', 'SVSFDefault',
    'IInternetSecurityMgrSite', 'UINT_PTR', 'DISPID_SRRAlternates',
    'SPSFunction', 'SAFT11kHz8BitStereo', 'ISpeechPhraseInfo',
    'DISPID_SPPFirstElement', 'SPWT_PRONUNCIATION',
    'DISPID_SRCResume', 'SAFTADPCM_11kHzStereo', 'SPBO_AHEAD',
    'SGDSInactive', 'DISPID_SLPType', 'SVEEndInputStream',
    'SITooFast', 'SPEI_PHONEME', 'SAFTCCITT_uLaw_22kHzMono',
    'DISPID_SBSSeek', 'SpeechRuleState', 'DISPID_SpeechBaseStream',
    'DISPID_SVSpeakStream', 'SAFT24kHz8BitStereo', 'SPVPRI_OVER',
    'SAFTCCITT_uLaw_22kHzStereo', 'DISPID_SRRSetTextFeedback',
    'eLEXTYPE_PRIVATE13', 'DISPID_SPEPronunciation',
    'SPEI_SENTENCE_BOUNDARY', 'SAFT44kHz16BitStereo',
    'SpeechFormatType', 'SPAS_CLOSED', 'DISPID_SRGId',
    'DISPID_SpeechVoiceEvent', 'DISPID_SGRSAddRuleTransition',
    'eLEXTYPE_PRIVATE15', 'DISPID_SASCurrentSeekPosition',
    'SDA_Two_Trailing_Spaces', 'SpeechPropertyResponseSpeed', 'SVP_4',
    'DISPID_SpeechGrammarRuleState',
    'DISPID_SRCAudioInInterferenceStatus',
    'DISPID_SPANumberOfElementsInResult',
    'DISPID_SpeechPhraseReplacement', 'SGLexical',
    'SAFTTrueSpeech_8kHz1BitMono', 'DISPID_SASFreeBufferSpace',
    'Speech_Max_Pron_Length', 'SRTSMLTimeout', 'SPXRO_SML',
    'SPWORDPRONUNCIATIONLIST', 'SPCT_DICTATION', 'ISpeechVoice',
    'SpeechCategoryPhoneConverters', 'DISPID_SpeechPhoneConverter',
    'ISpRecognizer', 'SPINTERFERENCE_NOISE', 'SVF_Stressed',
    'eLEXTYPE_PRIVATE17', 'SPEI_INTERFERENCE',
    'DISPID_SGRSTPropertyValue', 'DISPID_SPPs_NewEnum',
    'DISPID_SGRSTRule', 'SPRS_ACTIVE_USER_DELIMITED',
    '__MIDL___MIDL_itf_sapi_0000_0020_0001', 'SDTDisplayText',
    'ISpeechVoiceStatus', 'SpResourceManager',
    'ISpeechGrammarRuleStateTransitions', 'DISPID_SDKSetStringValue',
    'ISpMMSysAudio', 'DISPID_SGRSTWeight', 'SPSLMA', 'SINone',
    'DISPID_SRRGetXMLErrorInfo', 'SpCompressedLexicon',
    'SpMMAudioOut', 'SPGRAMMARWORDTYPE', 'SPCT_SUB_DICTATION',
    'DISPID_SPIRule', 'SPXMLRESULTOPTIONS',
    'DISPID_SpeechObjectTokenCategory', 'SVPAlert', 'ISpRecoContext2',
    'DISPID_SVSCurrentStreamNumber', 'SRESoundEnd',
    'DISPID_SpeechVoice', 'SPBO_TIME_UNITS', 'ISpPhrase',
    'SPSEMANTICFORMAT', 'DISPID_SPELexicalForm',
    'DISPID_SPERequiredConfidence', 'DISPID_SPEs_NewEnum',
    'DISPID_SPRText', 'SSFMOpenForRead', 'ISpEventSource',
    'SAFT8kHz16BitStereo', 'SAFT12kHz16BitStereo',
    'SAFTGSM610_22kHzMono', 'DISPID_SLWType', 'DISPID_SRSAudioStatus',
    'SVESentenceBoundary',
    'DISPID_SRAllowAudioInputFormatChangesOnNextSet',
    'SpeechEngineConfidence', 'SpeechAudioFormatType', 'DISPID_SOTId',
    'SAFT22kHz16BitMono', 'DISPID_SOTRemoveStorageFileName',
    'SpeechCategoryAppLexicons', 'SpeechRegistryLocalMachineRoot',
    'DISPID_SPEEngineConfidence', 'DISPID_SPIReplacements',
    'DISPID_SPRuleConfidence', 'SpeechRecoContextState',
    'SECFIgnoreWidth', 'DISPID_SRGCmdLoadFromResource', 'SRSInactive',
    'SVP_10', 'SPCONTEXTSTATE', 'SPSSuppressWord',
    'DISPID_SpeechPhraseRule', 'SVEWordBoundary',
    'SpeechDisplayAttributes', 'SPEI_ADAPTATION', 'DISPID_SRCVoice',
    'ISpeechFileStream', 'SDTRule', 'SAFTADPCM_8kHzMono', 'ISpStream',
    'ISpeechRecoResultDispatch',
    'SpeechPropertyLowConfidenceThreshold', 'DISPID_SOTCGetDataKey',
    'DISPID_SRCEInterference', 'DISPID_SpeechXMLRecoResult',
    'SRAExport', 'DISPID_SRCPause', 'DISPID_SDKCreateKey',
    'eLEXTYPE_USER', 'DISPID_SRRecognizer',
    'SPEI_PROPERTY_NUM_CHANGE', 'SPEI_RECO_STATE_CHANGE',
    'DISPID_SAFGuid', 'eLEXTYPE_RESERVED7', 'eLEXTYPE_RESERVED8',
    'SPADAPTATIONRELEVANCE', 'SPBINARYGRAMMAR', 'STSF_CommonAppData',
    'ISpObjectToken', 'SPEI_TTS_PRIVATE', 'DISPID_SVSkip',
    'SPRECORESULTTIMES', 'Speech_StreamPos_RealTime',
    'DISPID_SVSLastBookmark', 'SPSInterjection', 'SREAllEvents',
    'SSTTWildcard', 'SPAR_Unknown', 'ISpeechObjectTokenCategory',
    'DISPID_SPEsItem', 'DISPIDSPTSI_ActiveOffset',
    'DISPID_SRAudioInputStream', 'SP_VISEME_15', 'DISPID_SVSpeak',
    'SPPS_RESERVED3', 'DISPID_SRGCmdSetRuleState',
    'DISPID_SPEAudioSizeTime', 'DISPID_SRGRules',
    'ISpeechResourceLoader', 'SPPHRASERULE', 'DISPID_SDKDeleteKey',
    'SGLexicalNoSpecialChars', 'DISPID_SRCEAudioLevel',
    'ISpeechGrammarRule', 'SVEViseme', 'SPRULE', 'ISpVoice',
    'DISPID_SpeechGrammarRule', 'SP_VISEME_8',
    'DISPID_SADefaultFormat', 'eWORDTYPE_DELETED',
    'DISPIDSPTSI_ActiveLength', 'SPSNotOverriden', 'SSTTTextBuffer',
    'SPSUnknown', 'SLTUser', 'DISPID_SRGetRecognizers',
    'eLEXTYPE_PRIVATE5', 'DISPID_SpeechWaveFormatEx',
    'DISPID_SVEPhoneme', 'ISpShortcut', 'SpWaveFormatEx',
    'SPINTERFERENCE_LATENCY_TRUNCATE_END', 'eLEXTYPE_VENDORLEXICON',
    'DISPID_SPRsItem', 'SSSPTRelativeToEnd',
    'SAFTCCITT_ALaw_22kHzStereo', 'SPRS_INACTIVE', 'SREInterference',
    'ISpNotifySink', 'SDTAll', 'SpeechRetainedAudioOptions',
    'ISpeechAudio', 'eLEXTYPE_PRIVATE12', 'STCInprocHandler',
    'SAFTCCITT_uLaw_44kHzStereo', 'SAFTGSM610_11kHzMono',
    'eLEXTYPE_PRIVATE11', 'DISPID_SMSAMMHandle',
    'SWPUnknownWordUnpronounceable', 'SPAS_STOP', 'SPAO_NONE',
    'SDTProperty', 'DISPID_SPEAudioTimeOffset',
    'SpeechBookmarkOptions', 'SAFTCCITT_uLaw_8kHzStereo',
    'ISpeechWaveFormatEx', 'SAFT44kHz8BitStereo', 'SRCS_Enabled',
    'SpeechMicTraining', 'DISPID_SpeechLexiconPronunciation',
    'SP_VISEME_2', 'SpeechSpecialTransitionType', 'SVP_15',
    'SPWAVEFORMATTYPE', 'SAFT24kHz16BitStereo', 'SPPS_Noncontent',
    'SP_VISEME_1', 'eLEXTYPE_PRIVATE10'
]

