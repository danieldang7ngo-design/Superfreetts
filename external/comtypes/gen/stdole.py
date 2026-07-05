from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    FONTSTRIKETHROUGH, Default, OLE_YPOS_PIXELS, CoClass, dispid,
    OLE_XPOS_HIMETRIC, IFontEventsDisp, OLE_YSIZE_CONTAINER,
    DISPPARAMS, OLE_CANCELBOOL, Gray, IEnumVARIANT, BSTR,
    OLE_YSIZE_HIMETRIC, FONTSIZE, EXCEPINFO, Library, VgaColor,
    OLE_YSIZE_PIXELS, DISPMETHOD, IUnknown, OLE_XSIZE_CONTAINER, Font,
    IFontDisp, FONTUNDERSCORE, OLE_XSIZE_PIXELS, IFont, HRESULT,
    StdPicture, Unchecked, Picture, OLE_YPOS_CONTAINER,
    OLE_OPTEXCLUSIVE, GUID, FontEvents, FONTBOLD, FONTNAME,
    OLE_YPOS_HIMETRIC, OLE_HANDLE, OLE_XPOS_CONTAINER, Monochrome,
    OLE_COLOR, OLE_ENABLEDEFAULTBOOL, IPicture, OLE_XSIZE_HIMETRIC,
    FONTITALIC, VARIANT_BOOL, OLE_XPOS_PIXELS, StdFont, IDispatch,
    _lcid, Color, _check_version, DISPPROPERTY, typelib_path,
    COMMETHOD, IPictureDisp, Checked
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
    'FONTSTRIKETHROUGH', 'Default', 'StdPicture', 'FontEvents',
    'OLE_YPOS_PIXELS', 'OLE_XPOS_HIMETRIC', 'FONTBOLD',
    'IFontEventsDisp', 'OLE_YSIZE_CONTAINER', 'FONTNAME',
    'OLE_CANCELBOOL', 'Gray', 'OLE_YPOS_HIMETRIC', 'OLE_HANDLE',
    'OLE_XPOS_CONTAINER', 'Monochrome', 'OLE_COLOR',
    'OLE_ENABLEDEFAULTBOOL', 'Checked', 'IPicture',
    'OLE_YSIZE_HIMETRIC', 'FONTSIZE', 'OLE_XSIZE_HIMETRIC',
    'FONTITALIC', 'Library', 'VgaColor', 'OLE_YSIZE_PIXELS',
    'OLE_XPOS_PIXELS', 'LoadPictureConstants', 'StdFont',
    'OLE_XSIZE_CONTAINER', 'OLE_TRISTATE', 'Font', 'IFontDisp',
    'FONTUNDERSCORE', 'Color', 'OLE_XSIZE_PIXELS', 'IFont', 'Picture',
    'typelib_path', 'IPictureDisp', 'Unchecked', 'OLE_YPOS_CONTAINER',
    'OLE_OPTEXCLUSIVE'
]

