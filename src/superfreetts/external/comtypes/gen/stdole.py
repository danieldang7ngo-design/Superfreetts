from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    OLE_XSIZE_PIXELS, IFont, OLE_HANDLE, COMMETHOD, OLE_XPOS_HIMETRIC,
    OLE_CANCELBOOL, OLE_YSIZE_PIXELS, _lcid, OLE_OPTEXCLUSIVE,
    IEnumVARIANT, IPictureDisp, CoClass, OLE_YPOS_HIMETRIC,
    OLE_XPOS_PIXELS, Checked, IPicture, StdFont, DISPMETHOD, IUnknown,
    OLE_YSIZE_HIMETRIC, FONTSTRIKETHROUGH, OLE_XSIZE_CONTAINER,
    OLE_XSIZE_HIMETRIC, Default, FONTUNDERSCORE, OLE_XPOS_CONTAINER,
    VARIANT_BOOL, Gray, Library, DISPPARAMS, IFontDisp, BSTR, GUID,
    Monochrome, typelib_path, IFontEventsDisp, FontEvents, dispid,
    FONTNAME, FONTSIZE, OLE_YPOS_PIXELS, _check_version,
    OLE_ENABLEDEFAULTBOOL, OLE_YPOS_CONTAINER, FONTBOLD, Picture,
    HRESULT, VgaColor, Font, Color, DISPPROPERTY, Unchecked,
    StdPicture, OLE_COLOR, EXCEPINFO, FONTITALIC, IDispatch,
    OLE_YSIZE_CONTAINER
)


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


__all__ = [
    'OLE_XSIZE_PIXELS', 'IFontDisp', 'IFont', 'OLE_HANDLE',
    'Monochrome', 'OLE_XPOS_HIMETRIC', 'typelib_path',
    'OLE_CANCELBOOL', 'OLE_TRISTATE', 'IFontEventsDisp',
    'OLE_YSIZE_PIXELS', 'OLE_YSIZE_CONTAINER', 'FontEvents',
    'FONTNAME', 'FONTSIZE', 'OLE_OPTEXCLUSIVE', 'IPictureDisp',
    'LoadPictureConstants', 'OLE_YPOS_PIXELS', 'OLE_YPOS_HIMETRIC',
    'OLE_XPOS_PIXELS', 'OLE_ENABLEDEFAULTBOOL', 'Checked',
    'OLE_YPOS_CONTAINER', 'FONTBOLD', 'IPicture', 'Picture',
    'VgaColor', 'StdFont', 'Font', 'Color', 'FONTSTRIKETHROUGH',
    'OLE_XSIZE_CONTAINER', 'OLE_XSIZE_HIMETRIC', 'Unchecked',
    'StdPicture', 'Default', 'FONTUNDERSCORE', 'OLE_XPOS_CONTAINER',
    'OLE_COLOR', 'FONTITALIC', 'Gray', 'Library', 'OLE_YSIZE_HIMETRIC'
]

