#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

import pyds
import numpy as np
import cv2
import time

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        print("End-of-stream")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print("Warning: %s: %s\n" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

def main():
    # Initialize GStreamer
    Gst.init(None)

    # Create Pipeline
    pipeline = Gst.Pipeline()
    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
        return -1

    # Create Elements
    source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
    if not source:
        sys.stderr.write(" Unable to create Source \n")
        return -1

    caps_v4l2src = Gst.ElementFactory.make("capsfilter", "v4l2src_caps")
    if not caps_v4l2src:
        sys.stderr.write(" Unable to create v4l2src capsfilter \n")
        return -1

    # Set caps for the camera (adjust resolution if needed)
    caps_v4l2src.set_property('caps', Gst.Caps.from_string("video/x-raw, width=640, height=480, format=YUY2"))
    
    # Create nvvideoconvert for input
    nvvidconv_src = Gst.ElementFactory.make("nvvideoconvert", "convertor_src")
    if not nvvidconv_src:
        sys.stderr.write(" Unable to create nvvidconv_src \n")
        return -1
        
    # Add a memory type capsfilter
    nvvidconv_caps = Gst.ElementFactory.make("capsfilter", "nvmem_caps")
    if not nvvidconv_caps:
        sys.stderr.write(" Unable to create capsfilter \n")
        return -1
    
    # Set memory type capabilities
    nvvidconv_caps.set_property('caps', Gst.Caps.from_string("video/x-raw(memory:NVMM)"))

    # Create nvinfer
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")
        return -1

    # Create nvvideoconvert for output
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")
        return -1

    # Create OSD
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")
        return -1

    # Create video sink
    sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    if not sink:
        sys.stderr.write(" Unable to create egl sink \n")
        return -1

    # Set properties for inference
    pgie.set_property('config-file-path', '/home/usaas/Documents/CUDA-Project-ZERO/tests/Cam Test/peoplenet_config.txt')

    # Add elements to pipeline
    print("Adding elements to pipeline...")
    pipeline.add(source)
    pipeline.add(caps_v4l2src)
    pipeline.add(nvvidconv_src)
    pipeline.add(nvvidconv_caps)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)

    # Link elements
    print("Linking elements...")
    if not Gst.Element.link_many(source, caps_v4l2src, nvvidconv_src, nvvidconv_caps, pgie, nvvidconv, nvosd, sink):
        sys.stderr.write(" Elements could not be linked.\n")
        sys.exit(1)

    # Create event loop
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # Start pipeline
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    # Clean up
    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main())
