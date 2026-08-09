from enum import IntFlag

import comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 as __wrapper_module__
from comtypes.gen._C866CA3A_32F7_11D2_9602_00C04F8EE628_0_5_4 import (
    ISpShortcut, helpstring, SAFTCCITT_uLaw_8kHzMono,
    ISpeechPhraseAlternate, SPSModifier, DISPIDSPTSI_SelectionLength,
    ISpeechCustomStream, DISPID_SOTMatchesAttributes,
    DISPID_SPEDisplayText, SpTextSelectionInformation,
    DISPID_SDKEnumKeys, DISPID_SRGCmdSetRuleIdState, SPSHORTCUTPAIR,
    DISPID_SPRs_NewEnum, SRERequestUI, SSSPTRelativeToCurrentPosition,
    DISPID_SGRSTNextState, SPPS_RESERVED1, SPDKL_CurrentUser,
    SPSEMANTICERRORINFO, SPEI_MAX_TTS, DISPID_SVEPhoneme,
    SpeechAllElements, ISpeechTextSelectionInformation,
    ISpeechGrammarRules, Library, SVSFlagsAsync, BSTR,
    eLEXTYPE_PRIVATE14, DISPID_SRCPause, SLOStatic,
    DISPID_SPAs_NewEnum, dispid, SPINTERFERENCE_NONE,
    DISPID_SABufferInfo, SPPS_Noun, SAFTGSM610_11kHzMono,
    DISPID_SLGetPronunciations, SAFTCCITT_uLaw_11kHzMono, SPSHT_OTHER,
    DISPID_SGRSAddSpecialTransition, SPEI_ADAPTATION, SVP_15,
    SRCS_Enabled, DISPID_SGRAttributes, DISPID_SASNonBlockingIO,
    SRSActiveAlways, SPSMF_SRGS_SAPIPROPERTIES, SPSNoun,
    ISpeechAudioBufferInfo, ISpPhoneticAlphabetConverter,
    DISPID_SPRuleChildren, SpWaveFormatEx, SPSMF_UPS,
    DISPID_SRGCmdLoadFromProprietaryGrammar, eLEXTYPE_PRIVATE13,
    SpNullPhoneConverter, eLEXTYPE_PRIVATE7, SVPNormal,
    DISPID_SRCEPhraseStart, DISPID_SRCCmdMaxAlternates, SPWORDLIST,
    SVEWordBoundary, Speech_Max_Word_Length, SAFT8kHz8BitStereo,
    SRERecoOtherContext, ISpeechObjectTokens,
    SPINTERFERENCE_LATENCY_WARNING, ISpeechPhraseInfo,
    SpeechGrammarTagWildcard, SPRULE, DISPID_SRRAudio,
    DISPID_SLWPronunciations, SPBO_TIME_UNITS, SECFIgnoreCase,
    SRAExport, SAFTCCITT_uLaw_22kHzMono, DISPID_SRCEAudioLevel,
    STSF_LocalAppData, ISpSerializeState, DISPID_SRCRequestedUIType,
    SPBO_AHEAD, SPSLMA, ISpeechRecoResult, SpObjectToken,
    DISPID_SGRSAddWordTransition, SAFT8kHz8BitMono,
    DISPID_SOTRemoveStorageFileName, ISpeechPhraseReplacements,
    SP_VISEME_11, DISPID_SASFreeBufferSpace, DISPID_SPRulesItem,
    SpeechTokenKeyUI, SPEI_END_INPUT_STREAM, ISpRecoResult,
    SPWT_LEXICAL, SPSMF_SRGS_SEMANTICINTERPRETATION_MS, SVSFVoiceMask,
    DISPID_SGRClear, SDTReplacement, SAFT11kHz8BitMono, SPRS_ACTIVE,
    SPRECORESULTTIMES, SAFTCCITT_uLaw_44kHzStereo, DISPID_SVStatus,
    SDTAlternates, VARIANT, SAFTADPCM_44kHzMono,
    DISPID_SABIBufferSize, SAFT32kHz16BitMono, SpPhraseInfoBuilder,
    ISpeechPhraseElements, SpeechPropertyHighConfidenceThreshold,
    ISpeechPhraseInfoBuilder, SDKLLocalMachine, DISPID_SGRAddResource,
    eLEXTYPE_PRIVATE4, STSF_CommonAppData, DISPID_SGRSTPropertyName,
    SAFTADPCM_11kHzMono, ISpeechWaveFormatEx, SPAS_PAUSE,
    DISPID_SRAudioInputStream, DISPID_SVSCurrentStreamNumber,
    DISPID_SRCEPropertyNumberChange, ISpPhoneConverter,
    SpNotifyTranslator, SASClosed, DISPID_SLPLangId, SRAONone,
    SDTProperty, DISPID_SRSSupportedLanguages, SPPS_Verb,
    DISPID_SRRDiscardResultInfo, SREFalseRecognition, DISPID_SVVoice,
    ISpNotifyTranslator, SVP_14, SGRSTTTextBuffer,
    __MIDL___MIDL_itf_sapi_0000_0020_0001, DISPID_SGRsCommitAndSave,
    GUID, DISPID_SRAudioInput, eLEXTYPE_USER,
    __MIDL___MIDL_itf_sapi_0000_0020_0002, SASPause, DISPID_SGRId,
    DISPID_SPPEngineConfidence, ISpMMSysAudio, SWTAdded,
    ISpeechPhraseRules, SAFT8kHz16BitStereo, DISPID_SGRAddState,
    DISPID_SPAStartElementInResult, ISpProperties, SP_VISEME_10,
    DISPID_SLPType, SpVoice, SpCustomStream, SAFT44kHz16BitMono,
    SVP_4, SAFT48kHz16BitStereo, DISPID_SVSpeakStream, SVSFParseMask,
    ISpeechRecognizer, SPGS_ENABLED, ISpStreamFormatConverter,
    DISPID_SPERetainedStreamOffset, SpeechDictationTopicSpelling,
    SpeechTokenValueCLSID, SAFTCCITT_ALaw_44kHzStereo, SPEI_RESERVED1,
    DISPID_SGRSRule, ISpeechLexiconPronunciations,
    DISPID_SRCRetainedAudioFormat, DISPID_SPEAudioStreamOffset,
    DISPID_SWFEExtraData, eLEXTYPE_PRIVATE10,
    DISPID_SRCERecognizerStateChange, SPAS_CLOSED, SVEViseme,
    SPEI_SR_BOOKMARK, SAFT48kHz16BitMono, eLEXTYPE_RESERVED8,
    ISpRecoGrammar2, DISPID_SRRRecoContext, ISpeechMemoryStream,
    SPRST_ACTIVE_ALWAYS, IUnknown, SPWF_SRENGINE,
    DISPID_SRGDictationUnload, ISpObjectTokenCategory, ISpPhrase,
    SPCT_COMMAND, SVEAllEvents, DISPID_SRSAudioStatus,
    Speech_Default_Weight, DISPIDSPTSI_ActiveLength, DISPID_SRGRules,
    SPVPRI_NORMAL, SpeechTokenIdUserLexicon, STCInprocServer,
    DISPID_SRCCreateGrammar, SPEI_SR_RETAINEDAUDIO,
    DISPID_SVSLastResult, SpeechPropertyNormalConfidenceThreshold,
    SRSEDone, SPSERIALIZEDRESULT, Speech_StreamPos_RealTime,
    SREPhraseStart, SAFT22kHz16BitMono, eLEXTYPE_PRIVATE5,
    SECFIgnoreKanaType, SpeechAudioVolume, DISPID_SLWLangId,
    SPSMF_SAPI_PROPERTIES, eLEXTYPE_PRIVATE11, DISPID_SBSFormat,
    IStream, SPDKL_CurrentConfig, DISPID_SRCEEndStream,
    DISPID_SOTGetStorageFileName, DISPID_SASCurrentDevicePosition,
    SPEI_MIN_SR, DISPID_SOTId, ISpeechXMLRecoResult,
    SPEI_START_SR_STREAM, SFTInput, SVEAudioLevel, SRCS_Disabled,
    ISpObjectToken, SpUnCompressedLexicon, DISPID_SOTRemove,
    DISPID_SPRuleName, DISPID_SPRsItem, SREStreamStart,
    SAFT11kHz16BitMono, ISpEventSink, DISPID_SPIAudioSizeBytes,
    SPPS_RESERVED3, SRARoot, SpeechPropertyComplexResponseSpeed,
    ISpeechLexicon, DISPID_SMSALineId, ISpeechRecoGrammar,
    DISPID_SVWaitUntilDone, SP_VISEME_1, DISPID_SAFSetWaveFormatEx,
    SPEI_PROPERTY_STRING_CHANGE, SPEI_PHRASE_START, ISpVoice,
    SDTPronunciation, DISPID_SLWsItem, DISPID_SGRsItem,
    SPPHRASEPROPERTY, SAFTCCITT_uLaw_11kHzStereo, DISPID_SRStatus,
    SAFTADPCM_8kHzMono, SVSFParseSsml, SAFTCCITT_uLaw_8kHzStereo,
    SAFT24kHz8BitMono, SRTStandard, SPSHT_NotOverriden,
    SPFM_OPEN_READONLY, SECFIgnoreWidth, ISequentialStream,
    DISPID_SPPConfidence, SAFT22kHz8BitMono,
    SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE, SRSInactiveWithPurge,
    SREPropertyStringChange, SAFT22kHz8BitStereo, eLEXTYPE_PRIVATE15,
    ISpeechVoice, SPPHRASEREPLACEMENT, SPEI_VISEME, STSF_AppData,
    SDKLCurrentConfig, DISPID_SVGetProfiles, SPWORDPRONUNCIATIONLIST,
    SP_VISEME_0, STCAll, ISpeechLexiconWords, ISpRecoContext,
    SAFTGSM610_8kHzMono, DISPID_SGRSTsCount, SRAORetainAudio,
    DISPID_SVPriority, HRESULT, DISPID_SRRAlternates, SPAS_STOP,
    DISPID_SRCSetAdaptationData, ISpeechFileStream, SVPAlert,
    ISpStreamFormat, SRAInterpreter, DISPID_SVSInputWordPosition,
    SWPKnownWordPronounceable, SpStreamFormatConverter,
    DISPID_SPPFirstElement, SPEI_SR_PRIVATE, SECNormalConfidence,
    SPSHT_EMAIL, SRAImport, Speech_Max_Pron_Length, DISPID_SRCVoice,
    SPEI_TTS_BOOKMARK, DISPID_SRGSetTextSelection,
    DISPID_SGRsFindRule, SPVPRI_OVER, DISPID_SOTs_NewEnum,
    SDKLCurrentUser, SINoise, SPEI_RESERVED6,
    DISPID_SRGCmdSetRuleState, DISPID_SWFEAvgBytesPerSec, SPAR_High,
    DISPID_SLWType, SPRST_NUM_STATES, SVP_21, _LARGE_INTEGER,
    DISPID_SPPValue, SAFTNoAssignedFormat,
    DISPID_SPERequiredConfidence, SPINTERFERENCE_TOOFAST,
    SPINTERFERENCE_TOOQUIET, ISpeechGrammarRule,
    DISPID_SVSRunningState, SPEI_RESERVED3, DISPID_SWFEFormatTag,
    SAFT12kHz16BitStereo, DISPID_SPRuleEngineConfidence,
    DISPID_SRRGetXMLErrorInfo, SPSSuppressWord,
    DISPID_SRCRetainedAudio, DISPID_SRCEFalseRecognition,
    ISpeechGrammarRuleStateTransition, DISPID_SPEAudioSizeTime,
    SpStream, SPRST_INACTIVE, DISPID_SGRSTsItem,
    SPINTERFERENCE_LATENCY_TRUNCATE_END, DISPID_SPIEnginePrivateData,
    SPEI_SOUND_END, SPEI_ACTIVE_CATEGORY_CHANGED, SSFMOpenForRead,
    SpSharedRecoContext, SPPS_LMA, DISPID_SGRSTType, tagSTATSTG,
    SDTLexicalForm, _check_version, SPTEXTSELECTIONINFO,
    DISPID_SVEStreamEnd, DISPID_SPRules_NewEnum, ISpeechAudioFormat,
    SAFTCCITT_ALaw_22kHzMono, tagSPPROPERTYINFO, SAFT32kHz8BitStereo,
    SPAUDIOBUFFERINFO, SPSHORTCUTPAIRLIST, SpeechRegistryUserRoot,
    SPPS_RESERVED4, DISPID_SRGetPropertyString, SPWORD,
    DISPID_SPIRule, DISPID_SVAudioOutputStream,
    SAFTCCITT_ALaw_8kHzMono, DISPID_SRCEStartStream,
    DISPID_SRCESoundEnd, SGDSInactive, SVSFUnusedFlags,
    DISPID_SRSClsidEngine, wireHWND, SECFNoSpecialChars,
    DISPID_SGRInitialState, DISPID_SRCAudioInInterferenceStatus,
    SPAO_NONE, SpeechUserTraining, SpeechRegistryLocalMachineRoot,
    DISPID_SVIsUISupported, DISPID_SVSyncronousSpeakTimeout, SVP_6,
    ISpeechGrammarRuleStateTransitions, SAFTGSM610_22kHzMono,
    DISPID_SOTCGetDataKey, DISPID_SBSWrite, eLEXTYPE_USER_SHORTCUT,
    DISPID_SREmulateRecognition, SPEI_PHONEME, SREAudioLevel,
    SITooFast, DISPID_SRGId, SREInterference, SVF_Emphasis,
    SSSPTRelativeToEnd, DISPID_SVEEnginePrivate, DISPID_SLWsCount,
    ISpRecognizer2, DISPID_SAFType, SpSharedRecognizer,
    DISPID_SMSSetData, DISPID_SRState, SPRS_INACTIVE,
    SPEVENTSOURCEINFO, SPEI_PROPERTY_NUM_CHANGE, DISPID_SVSVisemeId,
    DISPID_SPEAudioSizeBytes, SpeechPropertyResponseSpeed, SVP_10,
    SpPhoneConverter, DISPID_SOTCId, DISPID_SRRTLength,
    DISPID_SPIGrammarId, DISPID_SOTCSetId, SAFT22kHz16BitStereo,
    ISpeechAudioStatus, SLODynamic, __MIDL_IWinTypes_0009,
    SRTSMLTimeout, SPSUnknown, SpMemoryStream, DISPID_SVResume,
    eLEXTYPE_PRIVATE9, SPCT_SLEEP, SPCS_DISABLED, DISPID_SASetState,
    DISPID_SWFEChannels, SGSEnabled, DISPID_SRRSetTextFeedback,
    SVEPhoneme, DISPID_SOTSetId, SFTSREngine, DISPID_SPIStartTime,
    SPINTERFERENCE_TOOLOUD, SPPS_SuppressWord, SAFTADPCM_22kHzStereo,
    SAFT12kHz16BitMono, SITooLoud, DISPID_SGRsCommit, SPPHRASERULE,
    SECHighConfidence, DISPID_SGRSAddRuleTransition, ISpeechDataKey,
    SVEVoiceChange, SVPOver, DISPID_SWFESamplesPerSec,
    DISPID_SCSBaseStream, DISPID_SRGState, SP_VISEME_6, SVP_1,
    DISPID_SRCBookmark, DISPID_SRSCurrentStreamNumber,
    DISPID_SRCCreateResultFromMemory, DISPID_SPIReplacements,
    SDA_No_Trailing_Space, SpeechPropertyResourceUsage,
    DISPID_SPIProperties, ISpGrammarBuilder, UINT_PTR, SGSDisabled,
    eLEXTYPE_PRIVATE18, ISpXMLRecoResult,
    DISPID_SRAllowVoiceFormatMatchingOnNextSet,
    DISPID_SVSInputWordLength, eLEXTYPE_PRIVATE6, eLEXTYPE_PRIVATE20,
    LONG_PTR, SP_VISEME_15, ISpResourceManager, SITooQuiet,
    SGDSActiveUserDelimited, SGLexicalNoSpecialChars, ISpNotifySink,
    SGSExclusive, SPINTERFERENCE_NOISE, SpeechCategoryPhoneConverters,
    DISPID_SRSCurrentStreamPosition, SpInProcRecoContext,
    DISPID_SPEsItem, SVP_12, SPAR_Unknown, ISpeechLexiconWord, _lcid,
    DISPID_SRCEEnginePrivate, DISPID_SPRuleFirstElement,
    IEnumSpObjectTokens, SRSActive, SAFT16kHz16BitMono,
    ISpeechMMSysAudio, ISpRecoCategory, SGRSTTWord, SP_VISEME_13,
    DISPID_SPEAudioTimeOffset, SpAudioFormat, SPEI_RESERVED2, SVP_9,
    DISPID_SGRSTPropertyId, SAFTCCITT_uLaw_22kHzStereo, SBOPause,
    DISPID_SASCurrentSeekPosition, SDTAudio, SPGS_EXCLUSIVE,
    DISPID_SRGCommit, DISPID_SGRSTRule, SPLO_DYNAMIC,
    SpeechRecoProfileProperties, SGDisplay, DISPID_SPPParent,
    SVF_Stressed, SRSEIsSpeaking, DISPID_SDKOpenKey,
    ISpeechLexiconPronunciation, DISPID_SRRTTickCount,
    DISPID_SLPsCount, SpeechCategoryVoices, ISpLexicon,
    DISPID_SPPNumberOfElements, SpLexicon, DISPID_SPIGetText,
    SPPS_Unknown, SDTAll, SAFTCCITT_uLaw_44kHzMono,
    DISPID_SRCreateRecoContext, SAFTGSM610_44kHzMono, SpMMAudioEnum,
    SPEI_START_INPUT_STREAM, SAFT12kHz8BitMono, SAFTDefault,
    SAFTCCITT_ALaw_8kHzStereo, SVP_0, SASRun, DISPID_SRRTStreamTime,
    SAFT24kHz16BitMono, SpCompressedLexicon, DISPID_SVSpeak,
    DISPID_SVESentenceBoundary, DISPID_SVEBookmark, DISPID_SPPsItem,
    SPDKL_LocalMachine, SAFT44kHz8BitStereo,
    DISPID_SLGetGenerationChange, ISpRecognizer3,
    DISPID_SOTCreateInstance, SpeechVoiceCategoryTTSRate, SVSFDefault,
    ULONG_PTR, SGRSTTWildcard, WAVEFORMATEX, SVEEndInputStream,
    DISPID_SPAsCount, ISpeechBaseStream, ISpEventSource, ISpPhraseAlt,
    DISPID_SPISaveToMemory, _ULARGE_INTEGER,
    DISPID_SRGCmdLoadFromResource, DISPID_SPEActualConfidence,
    eLEXTYPE_RESERVED4, SPFM_CREATE, _ISpeechVoiceEvents,
    SpeechVoiceSkipTypeSentence, SPEI_SOUND_START, SPGS_DISABLED,
    DISPID_SDKDeleteKey, DISPID_SRCERequestUI, DISPID_SBSRead,
    SAFTADPCM_44kHzStereo, DISPID_SRRPhraseInfo, eWORDTYPE_DELETED,
    SRERecognition, DISPID_SRCEHypothesis, SDA_One_Trailing_Space,
    SpFileStream, DISPID_SRCEventInterests, DISPID_SRCVoicePurgeEvent,
    ISpNotifySource, SP_VISEME_2, SITooSlow, SPXRO_Alternates_SML,
    DISPID_SPPChildren, DISPID_SVAudioOutput, SP_VISEME_3,
    DISPID_SABIEventBias, ISpeechPhoneConverter, SGLexical, SAFTText,
    eLEXTYPE_APP, ISpeechAudio, DISPID_SRGRecoContext,
    eLEXTYPE_PRIVATE12, eLEXTYPE_PRIVATE3, SSTTDictation,
    DISPID_SPPBRestorePhraseFromMemory, typelib_path,
    eLEXTYPE_PRIVATE8, SPWP_UNKNOWN_WORD_PRONOUNCEABLE,
    DISPID_SPRFirstElement, DISPID_SRIsShared, SREStreamEnd,
    DISPID_SPRulesCount, ISpeechObjectTokenCategory, SPSFunction,
    SDA_Consume_Leading_Spaces, DISPID_SPRNumberOfElements,
    DISPID_SPACommit, eLEXTYPE_PRIVATE19, DISPID_SPEsCount,
    DISPID_SPANumberOfElementsInResult, DISPID_SRSetPropertyNumber,
    SGPronounciation, SVP_16, DISPID_SLRemovePronunciation,
    DISPID_SRIsUISupported, SPAR_Low, DISPID_SPPsCount,
    SPSNotOverriden, SAFT48kHz8BitMono, DISPID_SOTIsUISupported,
    DISPID_SABIMinNotification, SDA_Two_Trailing_Spaces,
    SPEI_INTERFERENCE, SPPROPERTYINFO, SWPUnknownWordUnpronounceable,
    DISPID_SRCEBookmark, DISPID_SPIAudioStreamPosition, SPEI_MAX_SR,
    ISpeechResourceLoader, SECFEmulateResult, DISPID_SVEViseme,
    DISPID_SGRsCount, ISpStream, SVSFIsXML, SAFTADPCM_11kHzStereo,
    DISPID_SDKEnumValues, DISPIDSPTSI_SelectionOffset,
    eLEXTYPE_RESERVED10, STCRemoteServer, SpeechTokenKeyAttributes,
    ISpeechVoiceStatus, SP_VISEME_20, SPEI_END_SR_STREAM,
    DISPID_SPIRetainedSizeBytes, DISPID_SRProfile, DISPID_SRDisplayUI,
    SPEI_VOICE_CHANGE, SPEI_SENTENCE_BOUNDARY, SRESoundStart,
    SAFT44kHz16BitStereo, SpeechCategoryRecognizers,
    SAFT16kHz16BitStereo, DISPID_SVEventInterests,
    DISPID_SRGetRecognizers, DISPID_SGRSTText,
    SpPhoneticAlphabetConverter, DISPID_SPRsCount, DISPID_SRCResume,
    SAFTNonStandardFormat, SPDKL_DefaultLocation,
    DISPID_SRGDictationSetState, SECFDefault, DISPID_SPAsItem,
    DISPID_SDKSetStringValue, SPVPRI_ALERT, SP_VISEME_16,
    SPAUDIOSTATUS, eLEXTYPE_LETTERTOSOUND, DISPID_SLPPartOfSpeech,
    DISPID_SVGetAudioInputs, DISPID_SPRuleId, SPEI_TTS_PRIVATE,
    SPEI_TTS_AUDIO_LEVEL, DISPID_SVDisplayUI, DISPID_SRRTimes,
    DISPID_SGRsAdd, ISpDataKey, SGRSTTDictation, SVEPrivate,
    SRTAutopause, SpeechGrammarTagUnlimitedDictation,
    DISPID_SRGCmdLoadFromFile, DISPID_SGRSTPropertyValue,
    eLEXTYPE_RESERVED6, SVP_8, DISPID_SPCIdToPhone, SP_VISEME_14,
    SPPS_Function, Speech_StreamPos_Asap, SpResourceManager,
    SpeechAudioProperties, SPPHRASEELEMENT, SP_VISEME_7,
    DISPID_SOTDisplayUI, ISpeechObjectToken, SpeechTokenKeyFiles,
    SPRECOGNIZERSTATUS, SPCT_DICTATION, SPFM_NUM_MODES, SpMMAudioIn,
    SPLO_STATIC, SVP_5, DISPID_SPEs_NewEnum, DISPID_SRCEAdaptation,
    SBONone, ISpeechRecoResultTimes, DISPID_SPRuleParent,
    SPSHT_Unknown, SPEI_FALSE_RECOGNITION, DISPID_SOTGetAttribute,
    DISPID_SLPPhoneIds, SINoSignal, SVP_20, DISPID_SOTCategory,
    _RemotableHandle, SVP_13, DISPID_SGRs_NewEnum, SPPS_Interjection,
    SPEI_UNDEFINED, eLEXTYPE_PRIVATE17, SPEI_HYPOTHESIS, SPAR_Medium,
    DISPID_SRCESoundStart, SWTDeleted, SPSVerb,
    DISPID_SRCEPropertyStringChange, SVSFPurgeBeforeSpeak,
    SpMMAudioOut, STSF_FlagCreate, DISPID_SDKGetBinaryValue,
    DISPID_SWFEBitsPerSample, DISPID_SRGCmdLoadFromObject,
    DISPID_SPILanguageId, DISPID_SPPName, SpInprocRecognizer,
    SVEStartInputStream, DISPID_SPCLangId, SPRST_INACTIVE_WITH_PURGE,
    DISPID_SOTsCount, DISPID_SRCRecognizer, SPEI_SR_AUDIO_LEVEL,
    DISPID_SPEPronunciation, DISPID_SVSInputSentenceLength,
    SAFT44kHz8BitMono, SPBINARYGRAMMAR, SASStop, DISPID_SVGetVoices,
    SDTDisplayText, SpeechAudioFormatGUIDText, DISPID_SPRText,
    ISpeechRecoContext, DISPID_SFSClose, SRTExtendableParse,
    SAFT16kHz8BitStereo, SPWORDPRONUNCIATION, DISPID_SRRAudioFormat,
    DISPID_SRGCmdLoadFromMemory, SVP_11, SDTRule, DISPID_SVEWord,
    ISpAudio, SVP_17, DISPID_SPRuleConfidence,
    DISPID_SLRemovePronunciationByPhoneIds, eWORDTYPE_ADDED,
    SPINTERFERENCE_NOSIGNAL, DISPMETHOD, SDKLDefaultLocation,
    SPWP_KNOWN_WORD_PRONOUNCEABLE, DISPID_SPELexicalForm,
    DISPID_SVPause, SPINTERFERENCE_TOOSLOW,
    DISPID_SVAllowAudioOuputFormatChangesOnNextSet, VARIANT_BOOL,
    DISPID_SMSGetData, SREPrivate, SpeechGrammarTagDictation,
    DISPID_SVSInputSentencePosition, eLEXTYPE_MORPHOLOGY,
    eLEXTYPE_PRIVATE2, DISPID_SVSLastBookmarkId, SRESoundEnd,
    DISPID_SGRSTransitions, ISpRecoGrammar, SPRECOCONTEXTSTATUS,
    SINone, DISPID_SPIEngineId, SVP_3, SGDSActiveWithAutoPause,
    DISPID_SRAllowAudioInputFormatChangesOnNextSet, SPCS_ENABLED,
    ISpeechPhraseProperty, DISPID_SPRDisplayAttributes,
    eLEXTYPE_RESERVED7, SAFTTrueSpeech_8kHz1BitMono,
    SSFMCreateForWrite, SP_VISEME_18, IInternetSecurityManager,
    DISPID_SVSLastStreamNumberQueued, SPEI_RECO_STATE_CHANGE,
    DISPID_SDKSetLongValue, DISPID_SPPs_NewEnum,
    DISPID_SDKDeleteValue, IInternetSecurityMgrSite,
    SpObjectTokenCategory, IEnumString, SVP_18, DISPID_SAVolume,
    SPRS_ACTIVE_USER_DELIMITED, SPPS_RESERVED2,
    SAFTExtendedAudioFormat, eLEXTYPE_VENDORLEXICON,
    ISpeechPhraseReplacement, SWPUnknownWordPronounceable,
    DISPID_SLPsItem, COMMETHOD, SSTTWildcard, SRTReSent,
    DISPID_SWFEBlockAlign, SECLowConfidence, DISPID_SVRate,
    DISPID_SLPSymbolic, SVSFNLPSpeakPunc, SGRSTTRule,
    ISpeechRecoResultDispatch, SAFT32kHz16BitStereo,
    SAFT48kHz8BitStereo, DISPID_SRRecognizer, eLEXTYPE_PRIVATE16,
    DISPID_SPRuleNumberOfElements, SREStateChange,
    _ISpeechRecoContextEvents, DISPID_SPEDisplayAttributes,
    DISPID_SPARecoResult, DISPID_SRGSetWordSequenceData,
    DISPID_SOTCEnumerateTokens, SP_VISEME_12, SPPS_Modifier,
    SpeechCategoryRecoProfiles, DISPID_SLAddPronunciationByPhoneIds,
    SGRSTTEpsilon, SREAdaptation, DISPID_SVSkip, DISPID_SLWs_NewEnum,
    SPCT_SUB_DICTATION, DISPID_SGRSTWeight, DISPID_SVEVoiceChange,
    ISpeechPhraseElement, SPPS_NotOverriden, SPEI_MIN_TTS,
    SVSFParseAutodetect, SAFT24kHz8BitStereo,
    ISpPhoneticAlphabetSelection, ISpRecoContext2, IServiceProvider,
    SAFT12kHz8BitStereo, SVESentenceBoundary, DISPID_SPPId,
    DISPID_SMSAMMHandle, SLTUser, STCLocalServer,
    DISPID_SRSetPropertyString, DISPID_SRRSaveToMemory,
    SpeechPropertyAdaptationOn, SPWT_DISPLAY, SPEI_RESERVED5,
    SPWF_INPUT, tagSPTEXTSELECTIONINFO, SPVOICESTATUS,
    SPSMF_SRGS_SEMANTICINTERPRETATION_W3C, SpeechAddRemoveWord,
    DISPID_SPAPhraseInfo, DISPID_SLGenerationId, DISPID_SMSADeviceId,
    SPBO_PAUSE, WSTRING, eLEXTYPE_RESERVED9, DISPID_SRCERecognition,
    SRADefaultToActive, SpeechPropertyLowConfidenceThreshold,
    SPAS_RUN, DISPID_SGRName, SAFT32kHz8BitMono,
    DISPID_SVSpeakCompleteEvent, SAFTCCITT_ALaw_44kHzMono,
    DISPID_SRCERecognitionForOtherContext, DISPID_SADefaultFormat,
    DISPID_SPIElements, DISPID_SBSSeek, DISPID_SABufferNotifySize,
    DISPID_SGRSTs_NewEnum, SPSInterjection, DISPID_SAFGetWaveFormatEx,
    DISPID_SRGIsPronounceable, SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN,
    SPBO_NONE, SREBookmark, SSSPTRelativeToStart,
    ISpeechPhraseProperties, ISpeechRecoResult2, ISpRecognizer,
    SVSFIsFilename, DISPID_SFSOpen, DISPID_SVEAudioLevel,
    DISPID_SVGetAudioOutputs, SRATopLevel, _FILETIME,
    DISPID_SRRTOffsetFromStart, DISPID_SVEStreamStart,
    SAFT16kHz8BitMono, DISPID_SDKSetBinaryValue, DISPID_SVVolume,
    SPSERIALIZEDPHRASE, DISPID_SLWWord, DISPID_SPIAudioSizeTime,
    SPWT_PRONUNCIATION, SSFMOpenReadWrite, DISPID_SPEEngineConfidence,
    DISPID_SVSPhonemeId, SAFTADPCM_8kHzStereo, SREAllEvents, SPEVENT,
    DISPID_SVSLastBookmark, SpeechCategoryAppLexicons,
    DISPID_SRSNumberOfActiveRules, SpeechAudioFormatGUIDWave,
    SPWT_LEXICAL_NO_SPECIAL_CHARS, SP_VISEME_21,
    SpeechEngineProperties, DISPID_SRGetFormat, DISPID_SAEventHandle,
    DISPID_SOTGetDescription, SVP_19, DISPID_SPIGetDisplayAttributes,
    SpeechMicTraining, SAFTCCITT_ALaw_11kHzStereo, DISPID_SAStatus,
    DISPID_SOTsItem, SVP_7, SPFM_OPEN_READWRITE, DISPID_SOTCDefault,
    SLTApp, DISPID_SRCState, ISpeechPhraseAlternates,
    DISPID_SLGetWords, DISPID_SASState, SpeechCategoryAudioIn,
    SRSInactive, DISPID_SDKGetlongValue, DISPID_SRCEInterference,
    SSFMCreate, DISPID_SRGetPropertyNumber, DISPID_SPCPhoneToId,
    DISPID_SDKGetStringValue, DISPID_SDKCreateKey,
    DISPIDSPTSI_ActiveOffset, SpeechCategoryAudioOut,
    SPEI_WORD_BOUNDARY, STCInprocHandler, SpShortcut,
    eLEXTYPE_PRIVATE1, CoClass, DISPID_SPERetainedSizeBytes, SVF_None,
    DISPID_SGRsDynamic, SP_VISEME_8, SGDSActive,
    DISPID_SRRGetXMLResult, SPPS_Noncontent, SVSFParseSapi,
    SVSFPersistXML, DISPID_SRGDictationLoad, SVEBookmark,
    DISPID_SLPs_NewEnum, SPCT_SUB_COMMAND, ISpeechRecognizerStatus,
    ISpeechGrammarRuleState, SAFT8kHz16BitMono, SP_VISEME_5,
    SAFTCCITT_ALaw_11kHzMono, SP_VISEME_19, SPEI_REQUEST_UI,
    SRADynamic, SP_VISEME_9, SPEI_RECO_OTHER_CONTEXT, SPRST_ACTIVE,
    SP_VISEME_4, SPEI_RECOGNITION, DISPID_SAFGuid,
    SREPropertyNumChange, SPFM_CREATE_ALWAYS, SVP_2,
    DISPID_SRRSpeakAudio, SAFTADPCM_22kHzMono, SPAO_RETAIN_AUDIO,
    SP_VISEME_17, SAFT11kHz8BitStereo, SAFTCCITT_ALaw_22kHzStereo,
    SSTTTextBuffer, DISPID_SRGReset, SPXRO_SML, ISpObjectWithToken,
    SRTEmulated, DISPID_SVAlertBoundary, SAFT11kHz16BitStereo,
    DISPID_SOTDataKey, SREHypothesis, DISPID_SLAddPronunciation,
    SAFT24kHz16BitStereo, SVSFIsNotXML, ISpeechPhraseRule, SPPHRASE,
    SPRS_ACTIVE_WITH_AUTO_PAUSE, SVSFNLPMask
)


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


class SpeechStreamSeekPositionType(IntFlag):
    SSSPTRelativeToStart = 0
    SSSPTRelativeToCurrentPosition = 1
    SSSPTRelativeToEnd = 2


class SpeechAudioState(IntFlag):
    SASClosed = 0
    SASStop = 1
    SASPause = 2
    SASRun = 3


class SpeechSpecialTransitionType(IntFlag):
    SSTTWildcard = 1
    SSTTDictation = 2
    SSTTTextBuffer = 3


class SpeechEngineConfidence(IntFlag):
    SECLowConfidence = -1
    SECNormalConfidence = 0
    SECHighConfidence = 1


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


class SpeechStreamFileMode(IntFlag):
    SSFMOpenForRead = 0
    SSFMOpenReadWrite = 1
    SSFMCreate = 2
    SSFMCreateForWrite = 3


class SpeechRecognizerState(IntFlag):
    SRSInactive = 0
    SRSActive = 1
    SRSActiveAlways = 2
    SRSInactiveWithPurge = 3


class SpeechDisplayAttributes(IntFlag):
    SDA_No_Trailing_Space = 0
    SDA_One_Trailing_Space = 2
    SDA_Two_Trailing_Spaces = 4
    SDA_Consume_Leading_Spaces = 8


class SpeechRuleAttributes(IntFlag):
    SRATopLevel = 1
    SRADefaultToActive = 2
    SRAExport = 4
    SRAImport = 8
    SRAInterpreter = 16
    SRADynamic = 32
    SRARoot = 64


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


class SpeechBookmarkOptions(IntFlag):
    SBONone = 0
    SBOPause = 1


class SpeechFormatType(IntFlag):
    SFTInput = 0
    SFTSREngine = 1


class SpeechVoicePriority(IntFlag):
    SVPNormal = 0
    SVPAlert = 1
    SVPOver = 2


class SpeechRecognitionType(IntFlag):
    SRTStandard = 0
    SRTAutopause = 1
    SRTEmulated = 2
    SRTSMLTimeout = 4
    SRTExtendableParse = 8
    SRTReSent = 16


class SpeechLexiconType(IntFlag):
    SLTUser = 1
    SLTApp = 2


class SpeechWordType(IntFlag):
    SWTAdded = 1
    SWTDeleted = 2


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


class _SPAUDIOSTATE(IntFlag):
    SPAS_CLOSED = 0
    SPAS_STOP = 1
    SPAS_PAUSE = 2
    SPAS_RUN = 3


class SpeechInterference(IntFlag):
    SINone = 0
    SINoise = 1
    SINoSignal = 2
    SITooLoud = 3
    SITooQuiet = 4
    SITooFast = 5
    SITooSlow = 6


class SPSEMANTICFORMAT(IntFlag):
    SPSMF_SAPI_PROPERTIES = 0
    SPSMF_SRGS_SEMANTICINTERPRETATION_MS = 1
    SPSMF_SRGS_SAPIPROPERTIES = 2
    SPSMF_UPS = 4
    SPSMF_SRGS_SEMANTICINTERPRETATION_W3C = 8


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


class SPXMLRESULTOPTIONS(IntFlag):
    SPXRO_SML = 0
    SPXRO_Alternates_SML = 1


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


class SpeechRunState(IntFlag):
    SRSEDone = 1
    SRSEIsSpeaking = 2


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


class SPLOADOPTIONS(IntFlag):
    SPLO_STATIC = 0
    SPLO_DYNAMIC = 1


class SPRULESTATE(IntFlag):
    SPRS_INACTIVE = 0
    SPRS_ACTIVE = 1
    SPRS_ACTIVE_WITH_AUTO_PAUSE = 3
    SPRS_ACTIVE_USER_DELIMITED = 4


class SpeechGrammarWordType(IntFlag):
    SGDisplay = 0
    SGLexical = 1
    SGPronounciation = 2
    SGLexicalNoSpecialChars = 3


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


class SPAUDIOOPTIONS(IntFlag):
    SPAO_NONE = 0
    SPAO_RETAIN_AUDIO = 1


class SpeechVisemeFeature(IntFlag):
    SVF_None = 0
    SVF_Stressed = 1
    SVF_Emphasis = 2


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


class SPCATEGORYTYPE(IntFlag):
    SPCT_COMMAND = 0
    SPCT_DICTATION = 1
    SPCT_SLEEP = 2
    SPCT_SUB_COMMAND = 3
    SPCT_SUB_DICTATION = 4


class SPFILEMODE(IntFlag):
    SPFM_OPEN_READONLY = 0
    SPFM_OPEN_READWRITE = 1
    SPFM_CREATE = 2
    SPFM_CREATE_ALWAYS = 3
    SPFM_NUM_MODES = 4


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


class SPSHORTCUTTYPE(IntFlag):
    SPSHT_NotOverriden = -1
    SPSHT_Unknown = 0
    SPSHT_EMAIL = 4096
    SPSHT_OTHER = 8192
    SPPS_RESERVED1 = 12288
    SPPS_RESERVED2 = 16384
    SPPS_RESERVED3 = 20480
    SPPS_RESERVED4 = 61440


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


class SPWAVEFORMATTYPE(IntFlag):
    SPWF_INPUT = 0
    SPWF_SRENGINE = 1


class SPWORDTYPE(IntFlag):
    eWORDTYPE_ADDED = 1
    eWORDTYPE_DELETED = 2


class SPRECOSTATE(IntFlag):
    SPRST_INACTIVE = 0
    SPRST_ACTIVE = 1
    SPRST_ACTIVE_ALWAYS = 2
    SPRST_INACTIVE_WITH_PURGE = 3
    SPRST_NUM_STATES = 4


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


class SPGRAMMARWORDTYPE(IntFlag):
    SPWT_DISPLAY = 0
    SPWT_LEXICAL = 1
    SPWT_PRONUNCIATION = 2
    SPWT_LEXICAL_NO_SPECIAL_CHARS = 3


SPAUDIOSTATE = _SPAUDIOSTATE
SPSTREAMFORMATTYPE = SPWAVEFORMATTYPE


__all__ = [
    'SpeechVoiceSpeakFlags', 'SpInProcRecoContext', 'ISpShortcut',
    'DISPID_SPEsItem', 'SVP_12', 'DISPID_SpeechRecoContext',
    'SPAR_Unknown', 'SAFTCCITT_uLaw_8kHzMono', 'ISpeechLexiconWord',
    'ISpeechPhraseAlternate', 'DISPID_SRCEEnginePrivate',
    'DISPID_SPRuleFirstElement', 'SPSModifier',
    'DISPIDSPTSI_SelectionLength', 'IEnumSpObjectTokens',
    'ISpeechCustomStream', 'DISPID_SOTMatchesAttributes',
    'SpeechSpecialTransitionType', 'DISPID_SPEDisplayText',
    'SpTextSelectionInformation', 'SpeechRecognizerState',
    'SRSActive', 'DISPID_SDKEnumKeys', 'DISPID_SRGCmdSetRuleIdState',
    'SAFT16kHz16BitMono', 'SPSHORTCUTPAIR', 'DISPID_SPRs_NewEnum',
    'SRERequestUI', 'DISPID_SpeechGrammarRules', 'ISpeechMMSysAudio',
    'SSSPTRelativeToCurrentPosition', 'ISpRecoCategory',
    'DISPID_SGRSTNextState', 'SGRSTTWord', 'SP_VISEME_13',
    'DISPID_SPEAudioTimeOffset', 'SPPS_RESERVED1', 'SpAudioFormat',
    'SPEI_RESERVED2', 'DISPID_SpeechCustomStream', 'SVP_9',
    'DISPID_SGRSTPropertyId', 'SAFTCCITT_uLaw_22kHzStereo',
    'SPDKL_CurrentUser', 'SBOPause', 'SPSEMANTICERRORINFO',
    'DISPID_SASCurrentSeekPosition', 'SDTAudio', 'SPGS_EXCLUSIVE',
    'SPEI_MAX_TTS', 'SpeechLexiconType', 'DISPID_SVEPhoneme',
    'DISPID_SRGCommit', 'DISPID_SGRSTRule', 'SPLO_DYNAMIC',
    'SpeechRecoProfileProperties', 'SpeechAllElements', 'SGDisplay',
    'ISpeechTextSelectionInformation', 'DISPID_SPPParent',
    'SVF_Stressed', 'ISpeechGrammarRules', 'DISPID_SDKOpenKey',
    'SRSEIsSpeaking', 'ISpeechLexiconPronunciation', 'Library',
    'DISPID_SRRTTickCount', 'DISPID_SLPsCount', 'SVSFlagsAsync',
    'SpeechRecognitionType', 'DISPID_SpeechBaseStream',
    'SpeechCategoryVoices', 'SPSTREAMFORMATTYPE',
    'SpeechVoicePriority', 'DISPID_SpeechAudioFormat',
    'eLEXTYPE_PRIVATE14', 'ISpLexicon', 'SPEVENTENUM',
    'DISPID_SPPNumberOfElements', 'DISPID_SpeechVoiceStatus',
    'SpLexicon', 'DISPID_SPIGetText', 'DISPID_SRCPause', 'SLOStatic',
    'DISPID_SPAs_NewEnum', 'SpeechGrammarWordType', 'SPPS_Unknown',
    'SDTAll', 'SAFTCCITT_uLaw_44kHzMono',
    'DISPID_SRCreateRecoContext', 'SAFTGSM610_44kHzMono',
    'SpMMAudioEnum', '_SPAUDIOSTATE', 'SPINTERFERENCE_NONE',
    'SPEI_START_INPUT_STREAM', 'DISPID_SABufferInfo',
    'SAFT12kHz8BitMono', 'SAFTDefault', 'SPPS_Noun',
    'SAFTGSM610_11kHzMono', 'DISPID_SLGetPronunciations',
    'SpeechDataKeyLocation', 'SAFTCCITT_ALaw_8kHzStereo', 'SVP_0',
    'SASRun', 'DISPID_SRRTStreamTime', 'SAFT24kHz16BitMono',
    'SAFTCCITT_uLaw_11kHzMono', 'SpCompressedLexicon', 'SPSHT_OTHER',
    'DISPID_SVSpeak', 'DISPID_SVESentenceBoundary',
    'DISPID_SGRSAddSpecialTransition', 'SVP_15',
    'DISPID_SpeechLexiconWord', 'DISPID_SpeechRecoResult2',
    'SRCS_Enabled', 'SPEI_ADAPTATION', 'DISPID_SVEBookmark',
    'DISPID_SGRAttributes', 'DISPID_SPPsItem',
    'DISPID_SpeechPhraseProperties', 'SAFT44kHz8BitStereo',
    'SPDKL_LocalMachine', 'DISPID_SASNonBlockingIO',
    'DISPID_SLGetGenerationChange', 'DISPID_SpeechGrammarRule',
    'ISpRecognizer3', 'SRSActiveAlways', 'SPSMF_SRGS_SAPIPROPERTIES',
    'DISPID_SOTCreateInstance', 'SpeechVoiceCategoryTTSRate',
    'SVSFDefault', 'SGRSTTWildcard', 'WAVEFORMATEX',
    'SVEEndInputStream', 'DISPID_SPAsCount', 'SPSNoun',
    'ISpeechAudioBufferInfo', 'ISpPhoneticAlphabetConverter',
    'ISpeechBaseStream', 'SpWaveFormatEx', 'DISPID_SPRuleChildren',
    'SPSMF_UPS', 'DISPID_SRGCmdLoadFromProprietaryGrammar',
    'eLEXTYPE_PRIVATE13', 'DISPID_SpeechLexiconWords',
    'SpNullPhoneConverter', 'eLEXTYPE_PRIVATE7', 'SVPNormal',
    'DISPID_SRCEPhraseStart', 'ISpEventSource',
    'DISPID_SRCCmdMaxAlternates', 'ISpPhraseAlt',
    'DISPID_SPISaveToMemory', 'SPWORDLIST',
    'DISPID_SRGCmdLoadFromResource', 'SVEWordBoundary',
    'Speech_Max_Word_Length', 'DISPID_SPEActualConfidence',
    'eLEXTYPE_RESERVED4', 'DISPID_SpeechMemoryStream',
    'SPBOOKMARKOPTIONS', 'SpeechRuleAttributes', 'SPFM_CREATE',
    'SAFT8kHz8BitStereo', 'SRERecoOtherContext', 'SPVPRIORITY',
    '_ISpeechVoiceEvents', 'ISpeechObjectTokens',
    'SpeechVoiceSkipTypeSentence', 'SPEI_SOUND_START',
    'SPGS_DISABLED', 'DISPID_SDKDeleteKey', 'DISPID_SRCERequestUI',
    'DISPID_SBSRead', 'SAFTADPCM_44kHzStereo',
    'SPINTERFERENCE_LATENCY_WARNING', 'SpeechVisemeType',
    'SPAUDIOSTATE', 'DISPID_SRRPhraseInfo', 'eWORDTYPE_DELETED',
    'DISPID_SpeechXMLRecoResult', 'SRERecognition',
    'DISPID_SRCEHypothesis', 'SDA_One_Trailing_Space', 'SpFileStream',
    'DISPID_SRCEventInterests', 'DISPID_SRCVoicePurgeEvent',
    'ISpNotifySource', 'SPGRAMMARSTATE', 'ISpeechPhraseInfo',
    'SP_VISEME_2', 'SpeechGrammarTagWildcard', 'SITooSlow',
    'SPXRO_Alternates_SML', 'SPRULE', 'DISPID_SPPChildren',
    'DISPID_SRRAudio', 'DISPID_SLWPronunciations', 'SPBO_TIME_UNITS',
    'DISPID_SVAudioOutput', 'SP_VISEME_3', 'SpeechAudioFormatType',
    'DISPID_SABIEventBias', 'SECFIgnoreCase', 'SRAExport',
    'SAFTCCITT_uLaw_22kHzMono', 'DISPID_SRCEAudioLevel', 'SAFTText',
    'SGLexical', 'ISpeechPhoneConverter', 'STSF_LocalAppData',
    'DISPID_SRCRequestedUIType', 'eLEXTYPE_APP', 'ISpSerializeState',
    'ISpeechAudio', 'DISPID_SRGRecoContext', 'eLEXTYPE_PRIVATE12',
    'SPBO_AHEAD', 'SSTTDictation', 'SPSLMA', 'ISpeechRecoResult',
    'DISPID_SPPBRestorePhraseFromMemory', 'typelib_path',
    'eLEXTYPE_PRIVATE3', 'eLEXTYPE_PRIVATE8', 'SpObjectToken',
    'DISPID_SGRSAddWordTransition', 'SPWP_UNKNOWN_WORD_PRONOUNCEABLE',
    'DISPID_SPRFirstElement', 'SPSEMANTICFORMAT', 'DISPID_SRIsShared',
    'DISPID_SpeechAudio', 'SREStreamEnd', 'DISPID_SPRulesCount',
    'SAFT8kHz8BitMono', 'ISpeechObjectTokenCategory', 'SPSFunction',
    'SDA_Consume_Leading_Spaces', 'DISPID_SPRNumberOfElements',
    'DISPID_SOTRemoveStorageFileName', 'DISPID_SPACommit',
    'DISPID_SpeechDataKey', 'eLEXTYPE_PRIVATE19', 'DISPID_SPEsCount',
    'DISPID_SPANumberOfElementsInResult',
    'DISPID_SRSetPropertyNumber', 'SGPronounciation',
    'ISpeechPhraseReplacements', 'SVP_16',
    'DISPID_SLRemovePronunciation', 'SP_VISEME_11',
    'DISPID_SRIsUISupported', 'SPAR_Low', 'DISPID_SPPsCount',
    'SPSNotOverriden', 'DISPID_SASFreeBufferSpace',
    'DISPID_SPRulesItem', 'SpeechTokenKeyUI', 'SAFT48kHz8BitMono',
    'SpeechWordType', 'SPEI_END_INPUT_STREAM',
    'DISPID_SOTIsUISupported', 'ISpRecoResult',
    'DISPID_SABIMinNotification', 'SDA_Two_Trailing_Spaces',
    'SPEI_INTERFERENCE', 'SPPROPERTYINFO',
    'SPSMF_SRGS_SEMANTICINTERPRETATION_MS', 'SVSFVoiceMask',
    'SWPUnknownWordUnpronounceable', 'SPWT_LEXICAL',
    'DISPID_SRCEBookmark', 'DISPID_SPIAudioStreamPosition',
    'DISPID_SGRClear', 'SPEI_MAX_SR', 'ISpeechResourceLoader',
    'SECFEmulateResult', 'DISPID_SVEViseme', 'DISPID_SGRsCount',
    'ISpStream', 'SpeechTokenShellFolder', 'SVSFIsXML',
    'SDTReplacement', 'SAFT11kHz8BitMono', 'SPRS_ACTIVE',
    'SAFTADPCM_11kHzStereo', 'SPRECORESULTTIMES',
    'SAFTCCITT_uLaw_44kHzStereo', 'DISPID_SDKEnumValues',
    'DISPID_SVStatus', 'SDTAlternates', 'DISPID_SpeechWaveFormatEx',
    'SAFTADPCM_44kHzMono', 'DISPID_SABIBufferSize',
    'SAFT32kHz16BitMono', 'DISPIDSPTSI_SelectionOffset',
    'eLEXTYPE_RESERVED10', 'SpeechPropertyHighConfidenceThreshold',
    'SpPhraseInfoBuilder', 'STCRemoteServer', 'ISpeechPhraseElements',
    'SpeechTokenKeyAttributes', 'ISpeechPhraseInfoBuilder',
    'SDKLLocalMachine', 'SPSHORTCUTTYPE', 'DISPID_SGRAddResource',
    'eLEXTYPE_PRIVATE4', 'ISpeechVoiceStatus', 'STSF_CommonAppData',
    'DISPID_SGRSTPropertyName', 'SAFTADPCM_11kHzMono',
    'DISPID_SpeechLexiconProns', 'ISpeechWaveFormatEx',
    'SP_VISEME_20', 'SpeechTokenContext', 'SPAS_PAUSE',
    'SPLOADOPTIONS', 'SPEI_END_SR_STREAM',
    'DISPID_SPIRetainedSizeBytes', 'DISPID_SRProfile',
    'DISPID_SRAudioInputStream', 'DISPID_SRDisplayUI',
    'SPEI_VOICE_CHANGE', 'DISPID_SVSCurrentStreamNumber',
    'SRESoundStart', 'DISPID_SRCEPropertyNumberChange',
    'SpNotifyTranslator', 'SAFT44kHz16BitStereo',
    'SpeechCategoryRecognizers', 'SAFT16kHz16BitStereo',
    'SPEI_SENTENCE_BOUNDARY', 'DISPID_SVEventInterests', 'SASClosed',
    'ISpPhoneConverter', 'DISPID_SLPLangId', 'SRAONone',
    'SDTProperty', 'SpeechPartOfSpeech', 'DISPID_SRGetRecognizers',
    'DISPID_SRSSupportedLanguages', 'DISPID_SGRSTText',
    'SpPhoneticAlphabetConverter', 'SPPS_Verb',
    'DISPID_SRRDiscardResultInfo', 'DISPID_SPRsCount',
    'SREFalseRecognition', 'DISPID_SRCResume', 'DISPID_SVVoice',
    'SAFTNonStandardFormat', 'ISpNotifyTranslator', 'SVP_14',
    'SGRSTTTextBuffer', '__MIDL___MIDL_itf_sapi_0000_0020_0001',
    'DISPID_SpeechVoice', 'DISPID_SGRsCommitAndSave',
    'DISPID_SRAudioInput', 'DISPID_SRGDictationSetState',
    'SPDKL_DefaultLocation', 'SPAUDIOOPTIONS', 'eLEXTYPE_USER',
    'SpeechWordPronounceable', 'SECFDefault',
    '__MIDL___MIDL_itf_sapi_0000_0020_0002', 'DISPID_SPAsItem',
    'SASPause', 'DISPID_SGRId', 'DISPID_SPPEngineConfidence',
    'DISPID_SDKSetStringValue', 'SPCS_DISABLED', 'ISpMMSysAudio',
    'DISPID_SpeechObjectToken', 'SWTAdded',
    'DISPID_SpeechPhraseElements', 'ISpeechPhraseRules',
    'SAFT8kHz16BitStereo', 'DISPID_SGRAddState',
    'DISPID_SPAStartElementInResult', 'SPVPRI_ALERT', 'ISpProperties',
    'SP_VISEME_10', 'DISPID_SLPType', 'SpVoice', 'SP_VISEME_16',
    'SPAUDIOSTATUS', 'eLEXTYPE_LETTERTOSOUND', 'SpCustomStream',
    'SAFT44kHz16BitMono', 'SVP_4', 'SAFT48kHz16BitStereo',
    'DISPID_SLPPartOfSpeech', 'DISPID_SVGetAudioInputs',
    'DISPID_SPRuleId', 'SPEI_TTS_PRIVATE', 'DISPID_SVSpeakStream',
    'SPEI_TTS_AUDIO_LEVEL', 'DISPID_SVDisplayUI', 'DISPID_SRRTimes',
    'SVSFParseMask', 'DISPID_SGRsAdd', 'ISpeechRecognizer',
    'ISpDataKey', 'SPGS_ENABLED', 'SGRSTTDictation',
    'ISpStreamFormatConverter', 'DISPID_SPERetainedStreamOffset',
    'SpeechDictationTopicSpelling', 'SpeechTokenValueCLSID',
    'SVEPrivate', 'SRTAutopause',
    'SpeechGrammarTagUnlimitedDictation', 'DISPID_SRGCmdLoadFromFile',
    'DISPID_SGRSTPropertyValue', 'eLEXTYPE_RESERVED6', 'SVP_8',
    'SAFTCCITT_ALaw_44kHzStereo', 'DISPID_SPCIdToPhone',
    'SP_VISEME_14', 'SPEI_RESERVED1', 'DISPID_SGRSRule',
    'SPPS_Function', 'ISpeechLexiconPronunciations',
    'Speech_StreamPos_Asap', 'DISPID_SRCRetainedAudioFormat',
    'DISPID_SPEAudioStreamOffset', 'DISPID_SWFEExtraData',
    'eLEXTYPE_PRIVATE10', 'SpeechAudioProperties', 'SPPHRASEELEMENT',
    'DISPID_SRCERecognizerStateChange', 'SPCATEGORYTYPE',
    'SpResourceManager', 'SP_VISEME_7', 'SpeechInterference',
    'DISPID_SOTDisplayUI', 'SPAS_CLOSED', 'SpeechTokenKeyFiles',
    'SPRECOGNIZERSTATUS', 'ISpeechObjectToken', 'SVEViseme',
    'SPCT_DICTATION', 'SPFM_NUM_MODES', 'SPEI_SR_BOOKMARK',
    'SAFT48kHz16BitMono', 'SpMMAudioIn', 'SPLO_STATIC',
    'eLEXTYPE_RESERVED8', 'SVP_5', 'DISPID_SPEs_NewEnum',
    'ISpRecoGrammar2', 'DISPID_SRCEAdaptation',
    'DISPID_SRRRecoContext', 'SBONone', 'ISpeechRecoResultTimes',
    'DISPID_SPRuleParent', 'ISpeechMemoryStream', 'SPSHT_Unknown',
    'SPRST_ACTIVE_ALWAYS', 'SPEI_FALSE_RECOGNITION',
    'SPXMLRESULTOPTIONS', 'DISPID_SOTGetAttribute',
    'DISPID_SpeechPhraseElement', 'DISPID_SLPPhoneIds',
    'SPWF_SRENGINE', 'SINoSignal', 'SVP_20',
    'DISPID_SRGDictationUnload', 'DISPID_SOTCategory',
    'ISpObjectTokenCategory', '_RemotableHandle', 'ISpPhrase',
    'SPCT_COMMAND', 'SVP_13', 'SVEAllEvents', 'DISPID_SGRs_NewEnum',
    'DISPID_SRSAudioStatus', 'SpeechRecoContextState',
    'SPPS_Interjection', 'SPEI_UNDEFINED', 'Speech_Default_Weight',
    'DISPID_SpeechObjectTokens', 'eLEXTYPE_PRIVATE17',
    'DISPIDSPTSI_ActiveLength', 'DISPID_SRGRules', 'SPVPRI_NORMAL',
    'SpeechTokenIdUserLexicon', 'SPEI_HYPOTHESIS', 'STCInprocServer',
    'DISPID_SRCCreateGrammar', 'SPEI_SR_RETAINEDAUDIO', 'SPAR_Medium',
    'DISPID_SVSLastResult', 'SpeechPropertyNormalConfidenceThreshold',
    'DISPID_SRCESoundStart', 'SWTDeleted', 'SRSEDone',
    'SPEI_TTS_BOOKMARK', 'SPSVerb', 'DISPID_SRCEPropertyStringChange',
    'SVSFPurgeBeforeSpeak', 'SPSERIALIZEDRESULT',
    'Speech_StreamPos_RealTime', 'SREPhraseStart',
    'SAFT22kHz16BitMono', 'SpMMAudioOut', 'STSF_FlagCreate',
    'eLEXTYPE_PRIVATE5', 'DISPID_SDKGetBinaryValue',
    'DISPID_SWFEBitsPerSample', 'SECFIgnoreKanaType',
    'DISPID_SRGCmdLoadFromObject', 'SpeechAudioVolume',
    'DISPID_SLWLangId', 'DISPID_SPILanguageId', 'DISPID_SPPName',
    'SpInprocRecognizer', 'SPSMF_SAPI_PROPERTIES',
    'eLEXTYPE_PRIVATE11', 'SVEStartInputStream', 'DISPID_SPCLangId',
    'DISPID_SBSFormat', 'SPRST_INACTIVE_WITH_PURGE',
    'DISPID_SOTsCount', 'DISPID_SRSCurrentStreamPosition',
    'DISPID_SRCRecognizer', 'SPDKL_CurrentConfig', 'IStream',
    'DISPID_SRCEEndStream', 'DISPID_SOTGetStorageFileName',
    'DISPID_SASCurrentDevicePosition', 'SPEI_SR_AUDIO_LEVEL',
    'SPEI_MIN_SR', 'DISPID_SOTId', 'ISpeechXMLRecoResult',
    'DISPID_SPEPronunciation', 'SPEI_START_SR_STREAM',
    'DISPID_SVSInputSentenceLength', 'SAFT44kHz8BitMono',
    'SPBINARYGRAMMAR', 'DISPID_SpeechMMSysAudio',
    'DISPID_SpeechGrammarRuleState', 'SASStop', 'SFTInput',
    'DISPID_SVGetVoices', 'SVEAudioLevel', 'SRCS_Disabled',
    'SDTDisplayText', 'SpeechAudioFormatGUIDText', 'ISpObjectToken',
    'SpUnCompressedLexicon', 'DISPID_SPRText', 'DISPID_SOTRemove',
    'ISpeechRecoContext', 'DISPID_SFSClose', 'SRTExtendableParse',
    'DISPID_SPRuleName', 'DISPID_SPRsItem', 'SAFT16kHz8BitStereo',
    'SREStreamStart', 'SAFT11kHz16BitMono', 'ISpEventSink',
    'DISPID_SPIAudioSizeBytes', 'SPWORDPRONUNCIATION',
    'SpeechLoadOption', 'DISPID_SRRAudioFormat',
    'DISPID_SpeechVoiceEvent', 'SPPS_RESERVED3', 'SRARoot',
    'SpeechRunState', 'SpeechDisplayAttributes',
    'SpeechPropertyComplexResponseSpeed', 'SVP_11', 'ISpeechLexicon',
    'DISPID_SRGCmdLoadFromMemory', 'DISPID_SMSALineId',
    'ISpeechRecoGrammar', 'DISPID_SVWaitUntilDone', 'SP_VISEME_1',
    'SDTRule', 'DISPID_SVEWord', 'DISPID_SAFSetWaveFormatEx',
    'SVP_17', 'ISpAudio', 'DISPID_SPRuleConfidence',
    'DISPID_SLRemovePronunciationByPhoneIds', 'eWORDTYPE_ADDED',
    'SPEI_PROPERTY_STRING_CHANGE', 'SPEI_PHRASE_START',
    'DISPID_SpeechPhraseReplacement', 'SPGRAMMARWORDTYPE', 'ISpVoice',
    'SPINTERFERENCE_NOSIGNAL', 'SDTPronunciation', 'DISPID_SLWsItem',
    'DISPID_SGRsItem', 'SDKLDefaultLocation', 'SPPHRASEPROPERTY',
    'SPWP_KNOWN_WORD_PRONOUNCEABLE', 'SpeechVoiceEvents',
    'DISPID_SPELexicalForm', 'SAFTCCITT_uLaw_11kHzStereo',
    'DISPID_SVPause', 'DISPID_SRStatus', 'SPINTERFERENCE_TOOSLOW',
    'SAFTADPCM_8kHzMono', 'SpeechFormatType',
    'DISPID_SVAllowAudioOuputFormatChangesOnNextSet', 'SVSFParseSsml',
    'SAFTCCITT_uLaw_8kHzStereo', 'DISPID_SMSGetData',
    'SAFT24kHz8BitMono', 'SRTStandard', 'SpeechEmulationCompareFlags',
    'DISPID_SpeechGrammarRuleStateTransition', 'SREPrivate',
    'SpeechGrammarTagDictation', 'DISPID_SVSInputSentencePosition',
    'eLEXTYPE_MORPHOLOGY', 'eLEXTYPE_PRIVATE2', 'SPSHT_NotOverriden',
    'DISPID_SVSLastBookmarkId', 'SPFM_OPEN_READONLY', 'SRESoundEnd',
    'DISPID_SGRSTransitions', 'SECFIgnoreWidth', 'DISPIDSPTSI',
    'SPRECOCONTEXTSTATUS', 'DISPID_SpeechPhraseAlternates',
    'DISPID_SPPConfidence', 'ISpRecoGrammar', 'SAFT22kHz8BitMono',
    'SPWP_UNKNOWN_WORD_UNPRONOUNCEABLE', 'SINone',
    'SRSInactiveWithPurge', 'SREPropertyStringChange',
    'DISPID_SPIEngineId', 'SAFT22kHz8BitStereo', 'eLEXTYPE_PRIVATE15',
    'ISpeechVoice', 'SVP_3', 'SPPHRASEREPLACEMENT',
    'DISPID_SpeechPhraseBuilder', 'SGDSActiveWithAutoPause',
    'DISPID_SRAllowAudioInputFormatChangesOnNextSet', 'SPCS_ENABLED',
    'SPEI_VISEME', 'ISpeechPhraseProperty', 'STSF_AppData',
    'DISPID_SPRDisplayAttributes', 'SDKLCurrentConfig',
    'eLEXTYPE_RESERVED7', 'SAFTTrueSpeech_8kHz1BitMono',
    'DISPID_SVGetProfiles', 'SPWORDPRONUNCIATIONLIST',
    'DISPID_SpeechPhraseInfo', 'SSFMCreateForWrite', 'SP_VISEME_0',
    'STCAll', 'SP_VISEME_18', 'IInternetSecurityManager',
    'DISPID_SVSLastStreamNumberQueued', 'ISpeechLexiconWords',
    'SPEI_RECO_STATE_CHANGE', 'ISpRecoContext', 'SAFTGSM610_8kHzMono',
    'DISPID_SDKSetLongValue', 'DISPID_SGRSTsCount', 'SRAORetainAudio',
    'DISPID_SVPriority', 'DISPID_SPPs_NewEnum',
    'DISPID_SRRAlternates', 'SPAS_STOP', 'DISPID_SDKDeleteValue',
    'DISPID_SRCSetAdaptationData', 'ISpeechFileStream', 'SVPAlert',
    'ISpStreamFormat', 'SRAInterpreter',
    'DISPID_SVSInputWordPosition', 'IInternetSecurityMgrSite',
    'SpObjectTokenCategory', 'SWPKnownWordPronounceable',
    'SpStreamFormatConverter', 'IEnumString', 'SpeechRuleState',
    'DISPID_SPPFirstElement', 'SVP_18', 'SECNormalConfidence',
    'DISPID_SpeechAudioBufferInfo', 'SPSHT_EMAIL', 'SPEI_SR_PRIVATE',
    'DISPID_SAVolume', 'SRAImport', 'Speech_Max_Pron_Length',
    'DISPID_SRCVoice', 'DISPID_SRGSetTextSelection',
    'SPRS_ACTIVE_USER_DELIMITED', 'DISPID_SGRsFindRule',
    'SPPS_RESERVED2', 'SAFTExtendedAudioFormat',
    'eLEXTYPE_VENDORLEXICON', 'ISpeechPhraseReplacement',
    'SPVPRI_OVER', 'DISPID_SOTs_NewEnum', 'DISPID_SpeechRecoResult',
    'SWPUnknownWordPronounceable', 'SINoise', 'SDKLCurrentUser',
    'SPEI_RESERVED6', 'DISPID_SLPsItem', 'DISPID_SRGCmdSetRuleState',
    'SSTTWildcard', 'SRTReSent', 'DISPID_SWFEAvgBytesPerSec',
    'DISPID_SWFEBlockAlign', 'DISPID_SLWType', 'SPAR_High',
    'SPRST_NUM_STATES', 'SECLowConfidence', 'SVP_21', 'DISPID_SVRate',
    'DISPID_SLPSymbolic', 'SVSFNLPSpeakPunc', 'SGRSTTRule',
    'ISpeechRecoResultDispatch', 'SAFT32kHz16BitStereo',
    'DISPID_SPPValue', 'SAFTNoAssignedFormat', 'SAFT48kHz8BitStereo',
    'DISPID_SRRecognizer', 'eLEXTYPE_PRIVATE16',
    'DISPID_SPRuleNumberOfElements', 'SREStateChange',
    '_ISpeechRecoContextEvents', 'DISPID_SPEDisplayAttributes',
    'SPPARTOFSPEECH', 'DISPID_SPARecoResult',
    'DISPID_SPERequiredConfidence', 'DISPID_SRGSetWordSequenceData',
    'DISPID_SOTCEnumerateTokens', 'SP_VISEME_12', 'SPPS_Modifier',
    'SpeechCategoryRecoProfiles',
    'DISPID_SLAddPronunciationByPhoneIds', 'SPINTERFERENCE_TOOFAST',
    'SGRSTTEpsilon', 'SREAdaptation', 'DISPID_SVSkip',
    'DISPID_SLWs_NewEnum', 'SPCT_SUB_DICTATION',
    'SPINTERFERENCE_TOOQUIET', 'ISpeechGrammarRule',
    'DISPID_SVSRunningState', 'DISPID_SGRSTWeight', 'SPRULESTATE',
    'DISPID_SVEVoiceChange', 'ISpeechPhraseElement',
    'SPPS_NotOverriden', 'SPEI_MIN_TTS', 'SVSFParseAutodetect',
    'SAFT24kHz8BitStereo', 'SPEI_RESERVED3',
    'ISpPhoneticAlphabetSelection', 'ISpRecoContext2',
    'DISPID_SWFEFormatTag', 'SVESentenceBoundary',
    'SAFT12kHz8BitStereo', 'DISPID_SPPId', 'DISPID_SMSAMMHandle',
    'SLTUser', 'SAFT12kHz16BitStereo',
    'DISPID_SPRuleEngineConfidence', 'DISPID_SRRGetXMLErrorInfo',
    'SPADAPTATIONRELEVANCE', 'SPVISEMES', 'SPFILEMODE',
    'STCLocalServer', 'DISPID_SRSetPropertyString', 'SPSSuppressWord',
    'DISPID_SRCRetainedAudio', 'DISPID_SRCEFalseRecognition',
    'DISPID_SRRSaveToMemory', 'SpeechPropertyAdaptationOn',
    'DISPID_SpeechPhraseRules', 'ISpeechGrammarRuleStateTransition',
    'DISPID_SPEAudioSizeTime', 'SpStream', 'SPRST_INACTIVE',
    'SPWT_DISPLAY', 'DISPID_SGRSTsItem', 'SPEI_RESERVED5',
    'SPINTERFERENCE_LATENCY_TRUNCATE_END', 'SpeechEngineConfidence',
    'SpeechDiscardType', 'DISPID_SPIEnginePrivateData',
    'SPEI_SOUND_END', 'SPWF_INPUT', 'SPEI_ACTIVE_CATEGORY_CHANGED',
    'tagSPTEXTSELECTIONINFO', 'SPVOICESTATUS', 'SPWORDTYPE',
    'SPSMF_SRGS_SEMANTICINTERPRETATION_W3C', 'SSFMOpenForRead',
    'SpSharedRecoContext', 'SpeechAddRemoveWord', 'DISPID_SGRSTType',
    'DISPID_SPAPhraseInfo', 'tagSTATSTG', 'SDTLexicalForm',
    'SPPS_LMA', 'DISPID_SLGenerationId', 'SpeechBookmarkOptions',
    'DISPID_SMSADeviceId', 'SPBO_PAUSE', 'eLEXTYPE_RESERVED9',
    'SPTEXTSELECTIONINFO', 'DISPID_SVEStreamEnd',
    'DISPID_SPRules_NewEnum', 'ISpeechAudioFormat',
    'DISPID_SRCERecognition', 'SRADefaultToActive',
    'SpeechPropertyLowConfidenceThreshold', 'SPAS_RUN',
    'DISPID_SpeechRecoContextEvents', 'DISPID_SGRName',
    'SAFT32kHz8BitMono', 'SAFTCCITT_ALaw_22kHzMono',
    'DISPID_SVSpeakCompleteEvent', 'SAFT32kHz8BitStereo',
    'tagSPPROPERTYINFO', 'SAFTCCITT_ALaw_44kHzMono',
    'DISPID_SRCERecognitionForOtherContext',
    'SpeechRetainedAudioOptions', 'DISPID_SADefaultFormat',
    'DISPID_SpeechLexiconPronunciation', 'SPWAVEFORMATTYPE',
    'DISPID_SPIElements', 'DISPID_SBSSeek',
    'DISPID_SABufferNotifySize', 'DISPID_SGRSTs_NewEnum',
    'SPAUDIOBUFFERINFO', 'SPSInterjection', 'SPSHORTCUTPAIRLIST',
    'DISPID_SAFGetWaveFormatEx', 'SpeechRegistryUserRoot',
    'SPPS_RESERVED4', 'DISPID_SRGIsPronounceable',
    'DISPID_SRGetPropertyString',
    'SPINTERFERENCE_LATENCY_TRUNCATE_BEGIN', 'SPWORD',
    'DISPID_SPIRule', 'SPBO_NONE', 'SREBookmark',
    'SSSPTRelativeToStart', 'DISPID_SVAudioOutputStream',
    'ISpeechPhraseProperties', 'SAFTCCITT_ALaw_8kHzMono',
    'ISpeechRecoResult2', 'ISpRecognizer', 'SVSFIsFilename',
    'DISPID_SpeechPhraseRule', 'DISPID_SFSOpen',
    'DISPID_SVEAudioLevel', 'DISPID_SVGetAudioOutputs', 'SRATopLevel',
    'DISPID_SRCEStartStream', 'DISPID_SRCESoundEnd',
    'DISPID_SRRTOffsetFromStart', 'SPINTERFERENCE', 'SGDSInactive',
    'SVSFUnusedFlags', 'DISPID_SVEStreamStart',
    'DISPID_SRSClsidEngine', 'SAFT16kHz8BitMono',
    'DISPID_SDKSetBinaryValue', 'DISPID_SVVolume',
    'SPSERIALIZEDPHRASE', 'SECFNoSpecialChars', 'SpeechRecoEvents',
    'DISPID_SLWWord', 'DISPID_SGRInitialState',
    'DISPID_SRCAudioInInterferenceStatus', 'DISPID_SPIAudioSizeTime',
    'SpeechVisemeFeature', 'SPAO_NONE',
    'SpeechGrammarRuleStateTransitionType', 'SpeechUserTraining',
    'SpeechRegistryLocalMachineRoot', 'SPWT_PRONUNCIATION',
    'DISPID_SVIsUISupported', 'SSFMOpenReadWrite',
    'DISPID_SVSyncronousSpeakTimeout', 'DISPID_SPEEngineConfidence',
    'DISPID_SVSPhonemeId', 'DISPID_SpeechObjectTokenCategory',
    'SAFTADPCM_8kHzStereo', 'SREAllEvents', 'SVP_6', 'DISPIDSPRG',
    'SPEVENT', 'DISPID_SVSLastBookmark', 'SAFTGSM610_22kHzMono',
    'ISpeechGrammarRuleStateTransitions', 'DISPID_SOTCGetDataKey',
    'DISPID_SpeechRecognizer', 'SPLEXICONTYPE',
    'SpeechCategoryAppLexicons', 'DISPID_SBSWrite',
    'eLEXTYPE_USER_SHORTCUT', 'DISPID_SRSNumberOfActiveRules',
    'SpeechAudioFormatGUIDWave', 'DISPID_SREmulateRecognition',
    'SPWT_LEXICAL_NO_SPECIAL_CHARS', 'SPEI_PHONEME', 'SREAudioLevel',
    'SITooFast', 'SP_VISEME_21', 'SpeechEngineProperties',
    'DISPID_SRGId', 'SREInterference',
    'DISPID_SpeechGrammarRuleStateTransitions', 'SVF_Emphasis',
    'SSSPTRelativeToEnd', 'DISPID_SVEEnginePrivate',
    'DISPID_SLWsCount', 'ISpRecognizer2', 'DISPID_SAFType',
    'DISPID_SRGetFormat', 'SpSharedRecognizer', 'DISPID_SMSSetData',
    'DISPID_SAEventHandle', 'SpeechGrammarState', 'DISPID_SRState',
    'SPWORDPRONOUNCEABLE', 'DISPID_SOTGetDescription',
    'SPRS_INACTIVE', 'SVP_19', 'SPEVENTSOURCEINFO',
    'DISPID_SPIGetDisplayAttributes', 'SPEI_PROPERTY_NUM_CHANGE',
    'SpeechAudioState', 'SpeechMicTraining', 'DISPID_SVSVisemeId',
    'SAFTCCITT_ALaw_11kHzStereo', 'DISPID_SPEAudioSizeBytes',
    'DISPID_SAStatus', 'SpeechPropertyResponseSpeed', 'SVP_10',
    'SpPhoneConverter', 'DISPID_SOTsItem', 'SVP_7',
    'SpeechStreamSeekPositionType', 'DISPID_SOTCId',
    'DISPID_SpeechAudioStatus', 'DISPID_SRRTLength', 'SPRECOSTATE',
    'DISPID_SPIGrammarId', 'DISPID_SpeechPhraseAlternate',
    'DISPID_SOTCSetId', 'SPFM_OPEN_READWRITE', 'DISPID_SOTCDefault',
    'SAFT22kHz16BitStereo', 'SLTApp', 'DISPID_SRCState', 'SLODynamic',
    '__MIDL_IWinTypes_0009', 'ISpeechAudioStatus', 'SRTSMLTimeout',
    'SPSUnknown', 'SpMemoryStream', 'DISPID_SpeechFileStream',
    'DISPID_SASState', 'DISPID_SLGetWords', 'ISpeechPhraseAlternates',
    'DISPID_SVResume', 'SpeechCategoryAudioIn', 'eLEXTYPE_PRIVATE9',
    'SPCT_SLEEP', 'SRSInactive', 'DISPID_SDKGetlongValue',
    'DISPID_SASetState', 'DISPID_SWFEChannels',
    'DISPID_SRCEInterference', 'SGSEnabled', 'SSFMCreate',
    'DISPID_SRGetPropertyNumber', 'DISPID_SRRSetTextFeedback',
    'DISPID_SDKGetStringValue', 'DISPID_SDKCreateKey', 'SVEPhoneme',
    'DISPIDSPTSI_ActiveOffset', 'DISPID_SPCPhoneToId',
    'DISPID_SOTSetId', 'SpeechCategoryAudioOut', 'SPEI_WORD_BOUNDARY',
    'STCInprocHandler', 'SpShortcut', 'eLEXTYPE_PRIVATE1',
    'DISPID_SPERetainedSizeBytes', 'SFTSREngine',
    'DISPID_SPIStartTime', 'SPINTERFERENCE_TOOLOUD', 'SVF_None',
    'SPPS_SuppressWord', 'DISPID_SGRsDynamic',
    'SAFTADPCM_22kHzStereo', 'SPCONTEXTSTATE', 'SAFT12kHz16BitMono',
    'SP_VISEME_8', 'SITooLoud', 'DISPID_SGRsCommit', 'SGDSActive',
    'SPPHRASERULE', 'SECHighConfidence',
    'DISPID_SGRSAddRuleTransition', 'DISPID_SRRGetXMLResult',
    'SPPS_Noncontent', 'ISpeechDataKey', 'SVEVoiceChange',
    'SVSFParseSapi', 'SVPOver', 'SVSFPersistXML',
    'DISPID_SWFESamplesPerSec', 'DISPID_SRGDictationLoad',
    'SVEBookmark', 'DISPID_SLPs_NewEnum', 'SPCT_SUB_COMMAND',
    'ISpeechRecognizerStatus', 'ISpeechGrammarRuleState',
    'DISPID_SCSBaseStream', 'DISPID_SRGState', 'SP_VISEME_5',
    'SAFT8kHz16BitMono', 'SpeechStreamFileMode', 'SP_VISEME_6',
    'SAFTCCITT_ALaw_11kHzMono', 'SPDATAKEYLOCATION', 'SP_VISEME_19',
    'SPEI_REQUEST_UI', 'SVP_1', 'SRADynamic', 'DISPID_SRCBookmark',
    'DISPID_SRSCurrentStreamNumber', 'SP_VISEME_9',
    'DISPID_SRCCreateResultFromMemory', 'DISPID_SPIReplacements',
    'SDA_No_Trailing_Space', 'SPEI_RECO_OTHER_CONTEXT',
    'SpeechPropertyResourceUsage', 'SPRST_ACTIVE',
    'DISPID_SPIProperties', 'ISpGrammarBuilder', 'UINT_PTR',
    'SP_VISEME_4', 'SPEI_RECOGNITION', 'SGSDisabled',
    'eLEXTYPE_PRIVATE18', 'ISpXMLRecoResult',
    'SpeechCategoryPhoneConverters',
    'DISPID_SRAllowVoiceFormatMatchingOnNextSet',
    'DISPID_SVSInputWordLength', 'DISPID_SAFGuid',
    'SREPropertyNumChange', 'eLEXTYPE_PRIVATE6', 'SPFM_CREATE_ALWAYS',
    'eLEXTYPE_PRIVATE20', 'LONG_PTR', 'SP_VISEME_15', 'SVP_2',
    'DISPID_SpeechRecognizerStatus', 'DISPID_SRRSpeakAudio',
    'SAFTADPCM_22kHzMono', 'SPAO_RETAIN_AUDIO', 'SP_VISEME_17',
    'SAFT11kHz8BitStereo', 'SAFTCCITT_ALaw_22kHzStereo',
    'ISpResourceManager', 'SSTTTextBuffer', 'DISPID_SRGReset',
    'SITooQuiet', 'DISPID_SpeechRecoResultTimes',
    'SGDSActiveUserDelimited', 'SPXRO_SML', 'ISpObjectWithToken',
    'SRTEmulated', 'SGLexicalNoSpecialChars',
    'DISPID_SVAlertBoundary', 'DISPID_SpeechPhraseReplacements',
    'ISpNotifySink', 'SAFT11kHz16BitStereo', 'DISPID_SOTDataKey',
    'SREHypothesis', 'DISPID_SLAddPronunciation',
    'SAFT24kHz16BitStereo', 'SGSExclusive', 'SVSFIsNotXML',
    'DISPID_SpeechPhraseProperty', 'DISPID_SpeechPhoneConverter',
    'SPPHRASE', 'SPRS_ACTIVE_WITH_AUTO_PAUSE', 'ISpeechPhraseRule',
    'SPINTERFERENCE_NOISE', 'DISPID_SpeechLexicon', 'SVSFNLPMask'
]

