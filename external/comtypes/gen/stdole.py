from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    OLE_YPOS_CONTAINER, OLE_XSIZE_CONTAINER, FONTSTRIKETHROUGH,
    Picture, IFontEventsDisp, BSTR, IFont, Library, FONTITALIC,
    COMMETHOD, _check_version, FONTBOLD, Gray, HRESULT, Default,
    DISPPROPERTY, StdFont, VgaColor, EXCEPINFO, _lcid,
    OLE_YSIZE_HIMETRIC, VARIANT_BOOL, IPicture, OLE_YSIZE_PIXELS,
    IUnknown, OLE_YPOS_HIMETRIC, Monochrome, FontEvents, Checked,
    OLE_YSIZE_CONTAINER, OLE_XSIZE_PIXELS, OLE_YPOS_PIXELS,
    OLE_XPOS_CONTAINER, FONTNAME, OLE_XPOS_PIXELS,
    OLE_ENABLEDEFAULTBOOL, IFontDisp, StdPicture, DISPPARAMS,
    OLE_XSIZE_HIMETRIC, IDispatch, FONTSIZE, FONTUNDERSCORE,
    DISPMETHOD, IEnumVARIANT, OLE_COLOR, Font, OLE_CANCELBOOL,
    OLE_HANDLE, dispid, IPictureDisp, Unchecked, Color,
    OLE_OPTEXCLUSIVE, GUID, typelib_path, CoClass, OLE_XPOS_HIMETRIC
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
    'OLE_YSIZE_CONTAINER', 'OLE_XSIZE_PIXELS', 'OLE_YPOS_CONTAINER',
    'OLE_XSIZE_CONTAINER', 'FONTSTRIKETHROUGH', 'Picture',
    'IFontEventsDisp', 'OLE_YPOS_PIXELS', 'IFont', 'Library',
    'FONTITALIC', 'Monochrome', 'OLE_XPOS_CONTAINER', 'FONTNAME',
    'OLE_XPOS_PIXELS', 'OLE_ENABLEDEFAULTBOOL',
    'LoadPictureConstants', 'FONTBOLD', 'OLE_TRISTATE', 'IFontDisp',
    'Gray', 'Default', 'StdPicture', 'OLE_XSIZE_HIMETRIC', 'FONTSIZE',
    'FONTUNDERSCORE', 'OLE_COLOR', 'StdFont', 'Font',
    'OLE_CANCELBOOL', 'OLE_HANDLE', 'VgaColor', 'IPictureDisp',
    'Unchecked', 'Color', 'OLE_YSIZE_HIMETRIC', 'OLE_OPTEXCLUSIVE',
    'typelib_path', 'IPicture', 'OLE_YSIZE_PIXELS',
    'OLE_XPOS_HIMETRIC', 'OLE_YPOS_HIMETRIC', 'FontEvents', 'Checked'
]

