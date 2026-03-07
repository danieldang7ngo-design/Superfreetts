from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    CoClass, OLE_YPOS_HIMETRIC, FONTSTRIKETHROUGH, IFontDisp,
    OLE_COLOR, OLE_XSIZE_HIMETRIC, Color, OLE_XPOS_HIMETRIC,
    FONTUNDERSCORE, FontEvents, Monochrome, OLE_YPOS_CONTAINER,
    DISPMETHOD, Font, IEnumVARIANT, COMMETHOD, OLE_YSIZE_HIMETRIC,
    DISPPARAMS, OLE_XSIZE_CONTAINER, OLE_YSIZE_PIXELS, IPicture,
    IFont, DISPPROPERTY, Library, OLE_YPOS_PIXELS, GUID,
    OLE_ENABLEDEFAULTBOOL, StdFont, BSTR, Default, OLE_OPTEXCLUSIVE,
    typelib_path, IPictureDisp, FONTITALIC, OLE_XPOS_PIXELS, FONTSIZE,
    Checked, OLE_HANDLE, VgaColor, FONTBOLD, _check_version,
    OLE_CANCELBOOL, dispid, IDispatch, VARIANT_BOOL, _lcid, FONTNAME,
    StdPicture, Gray, Picture, IFontEventsDisp, Unchecked, IUnknown,
    OLE_YSIZE_CONTAINER, EXCEPINFO, OLE_XSIZE_PIXELS, HRESULT,
    OLE_XPOS_CONTAINER
)


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


__all__ = [
    'OLE_YPOS_HIMETRIC', 'FONTSTRIKETHROUGH', 'IFontDisp',
    'OLE_YPOS_PIXELS', 'OLE_COLOR', 'OLE_XSIZE_HIMETRIC', 'Color',
    'OLE_ENABLEDEFAULTBOOL', 'StdFont', 'Default',
    'OLE_XPOS_HIMETRIC', 'FONTUNDERSCORE', 'OLE_OPTEXCLUSIVE',
    'typelib_path', 'FontEvents', 'FONTITALIC', 'IPictureDisp',
    'Monochrome', 'OLE_YPOS_CONTAINER', 'OLE_XPOS_PIXELS',
    'OLE_TRISTATE', 'FONTSIZE', 'Font', 'OLE_YSIZE_HIMETRIC',
    'LoadPictureConstants', 'Checked', 'OLE_XSIZE_CONTAINER',
    'OLE_HANDLE', 'VgaColor', 'FONTBOLD', 'OLE_CANCELBOOL',
    'FONTNAME', 'StdPicture', 'Gray', 'Picture', 'IFontEventsDisp',
    'OLE_YSIZE_PIXELS', 'Unchecked', 'OLE_YSIZE_CONTAINER',
    'OLE_XSIZE_PIXELS', 'IPicture', 'OLE_XPOS_CONTAINER', 'IFont',
    'Library'
]

