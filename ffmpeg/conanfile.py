from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


EMCC_PATCH = """
diff --git a/libavcodec/log2_tab.c b/libavcodec/log2_tab.c
index 47a1df0..e415363 100644
--- a/libavcodec/log2_tab.c
+++ b/libavcodec/log2_tab.c
@@ -1 +1,2 @@
-#include "libavutil/log2_tab.c"
+#define ff_log2_tab ff_log2_tab_avcodec
+# include "libavutil/log2_tab.c"
diff --git a/libavcodec/reverse.c b/libavcodec/reverse.c
index 440bada..c7b3ca0 100644
--- a/libavcodec/reverse.c
+++ b/libavcodec/reverse.c
@@ -1 +1,2 @@
-#include "libavutil/reverse.c"
+#define ff_reverse ff_reverse_avutil
+# include "libavutil/reverse.c"
diff --git a/libavfilter/log2_tab.c b/libavfilter/log2_tab.c
index 47a1df0..db4d753 100644
--- a/libavfilter/log2_tab.c
+++ b/libavfilter/log2_tab.c
@@ -1 +1,2 @@
-#include "libavutil/log2_tab.c"
+#define ff_log2_tab ff_log2_tab_avfilter
+# include "libavutil/log2_tab.c"
diff --git a/libswresample/log2_tab.c b/libswresample/log2_tab.c
index 47a1df0..88d5f40 100644
--- a/libswresample/log2_tab.c
+++ b/libswresample/log2_tab.c
@@ -1 +1,2 @@
-#include "libavutil/log2_tab.c"
+#define ff_log2_tab ff_log2_tab_swresample
+# include "libavutil/log2_tab.c"
diff --git a/libswscale/log2_tab.c b/libswscale/log2_tab.c
index 47a1df0..7b0cb50 100644
--- a/libswscale/log2_tab.c
+++ b/libswscale/log2_tab.c
@@ -1 +1,2 @@
-#include "libavutil/log2_tab.c"
+#define ff_log2_tab ff_log2_tab_swscale
+# include "libavutil/log2_tab.c"
diff --git a/libavformat/golomb_tab.c b/libavformat/golomb_tab.c
index 063fae3647..384dec8557 100644
--- a/libavformat/golomb_tab.c
+++ b/libavformat/golomb_tab.c
@@ -1 +1 @@
-#include "libavcodec/golomb.c"
+#define ff_golomb_vlc_len ff_golomb_vlc_len_avformat
diff --git a/libavformat/log2_tab.c b/libavformat/log2_tab.c
index 47a1df03b7..0115bbe2ff 100644
--- a/libavformat/log2_tab.c
+++ b/libavformat/log2_tab.c
@@ -1 +1 @@
-#include "libavutil/log2_tab.c"
+#define ff_log2_tab ff_log2_tab_avformat
"""


class FfmpegConan(ConanFile):
    name = "Ffmpeg"
    version = "3.4.0-43"
    source_version = "n3.4"
    license = "LGPL"
    url = "https://ffmpeg.org/"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [
        True, False], "emcc": [True, False]}
    default_options = "shared=False", "fPIC=False", "emcc=False"
    requires = "Libvpx/1.6.1-40@satorivideo/master", "Zlib/1.2.11-40@satorivideo/master", "Bzip2/1.0.6-40@satorivideo/master"

    def requirements(self):
        self.options["Libvpx"].shared = self.options.shared
        self.options["Libvpx"].fPIC = self.options.fPIC
        self.options["Libvpx"].emcc = self.options.emcc
        self.options["Zlib"].shared = self.options.shared
        self.options["Zlib"].fPIC = self.options.fPIC
        self.options["Bzip2"].shared = self.options.shared
        self.options["Bzip2"].fPIC = self.options.fPIC

    def source(self):
        self.run(
            "git clone --depth 1 -b %s https://github.com/FFmpeg/FFmpeg.git" % self.source_version)

    def build(self):
        if self.options.emcc:
            self.output.info("Applying emcc patch")
            tools.patch(patch_string=EMCC_PATCH,
                        base_path="FFmpeg")

        configure_cmd = "./configure"
        configure_args = []

        prefix = os.path.abspath("install")
        configure_args.append("--prefix=%s" % prefix)
        if self.options.fPIC:
            configure_args.append("--enable-pic")
        if self.options.shared:
            configure_args.append("--enable-shared")
        if self.settings.build_type == "Debug":
            configure_args.append("--enable-debug=3")
            configure_args.append("--disable-stripping")

        # disable as much as possible
        configure_args.append("--disable-all")
        configure_args.append("--disable-programs")
        configure_args.append("--disable-everything")
        configure_args.append("--disable-sdl2")

        # enable libraries
        configure_args.append("--enable-avcodec")
        configure_args.append("--enable-avdevice")
        configure_args.append("--enable-avfilter")
        configure_args.append("--enable-avformat")
        configure_args.append("--enable-avutil")
        configure_args.append("--enable-swscale")
        configure_args.append("--enable-indev=avfoundation")

        # enable codecs
        configure_args.append("--enable-libvpx")
        configure_args.append("--enable-decoder=h264")
        configure_args.append("--enable-decoder=mjpeg")
        configure_args.append("--enable-decoder=libvpx_vp8")
        configure_args.append("--enable-decoder=libvpx_vp9")
        configure_args.append("--enable-encoder=libvpx_vp9")
        configure_args.append("--enable-decoder=rawvideo")
        configure_args.append("--enable-encoder=jpeg2000")
        configure_args.append("--enable-encoder=mjpeg")
        configure_args.append("--enable-encoder=srt")
        configure_args.append("--enable-bsf=vp9_superframe")
        
        # (de)muxers
        configure_args.append("--enable-demuxer=mov")
        configure_args.append("--enable-demuxer=matroska")
        configure_args.append("--enable-demuxer=webm")
        configure_args.append("--enable-demuxer=rtsp")
        configure_args.append("--enable-demuxer=flv")
        configure_args.append("--enable-demuxer=mjpeg")
        configure_args.append("--enable-muxer=matroska")
        configure_args.append("--enable-muxer=mp4")

        # protocols
        configure_args.append("--enable-protocol=file")
        configure_args.append("--enable-protocol=http")
        configure_args.append("--enable-protocol=https")
        configure_args.append("--enable-protocol=rtp")
        configure_args.append("--enable-protocol=rtmp")
        
        # parsers
        configure_args.append("--enable-parser=h264")
        configure_args.append("--enable-parser=mjpeg")
        configure_args.append("--enable-parser=vp8")
        configure_args.append("--enable-parser=vp9")

        # filters
        filters = self.get_video_filters()
        configure_args.append("--enable-filter=" + ','.join(filters))

        if self.options.emcc:
            if not self.options.shared:
                raise Exception(
                    "emcc should be used with shared libraries only.")
            configure_cmd = "emconfigure %s" % configure_cmd
            configure_args.append("--enable-cross-compile")
            configure_args.append("--target-os=none")
            configure_args.append("--arch=x86")
            configure_args.append("--disable-asm")
            configure_args.append("--disable-runtime-cpudetect")
            configure_args.append("--disable-fast-unaligned")
            configure_args.append("--disable-pthreads")
            configure_args.append("--disable-static")
            configure_args.append("--enable-shared")
            configure_args.append("--disable-stripping")

        if self.settings.build_type == "Debug":
            configure_args.append("--enable-debug=3")
            configure_args.append("--disable-stripping")

        if "CC" in os.environ:
            configure_args.append("--cc=\"%s\"" % os.environ["CC"])
        if "CXX" in os.environ:
            configure_args.append("--cxx=\"%s\"" % os.environ["CXX"])
        if "CFLAGS" in os.environ:
            configure_args.append("--extra-cflags=\"%s\"" % os.environ["CFLAGS"])
        if "CXXFLAGS" in os.environ:
            configure_args.append("--extra-cxxflags=\"%s\"" % os.environ["CXXFLAGS"])
        if "LDFLAGS" in os.environ:
            configure_args.append("--extra-ldflags=\"%s\"" % os.environ["LDFLAGS"])

        env_build = AutoToolsBuildEnvironment(self)
        env_vars = dict(env_build.vars)
        with tools.environment_append(env_vars):
            self.output.info("Build environment: %s" % env_vars)
            self.output.info("%s %s" %
                             (configure_cmd, " ".join(configure_args)))
            self.run("cd FFmpeg && %s %s" %
                     (configure_cmd, " ".join(configure_args)))

            self.run("cd FFmpeg && V=1 make -j%s all install" %
                     tools.cpu_count())

    def package(self):
        self.copy("*", src="install")

    def package_info(self):
        self.cpp_info.libs = ["avdevice", "avfilter", "swscale",
                              "avformat", "avcodec", "avutil",
                              "pthread", "dl"]

        if self.settings.os == "Macos":
            self.cpp_info.libs.append("iconv")
            self.cpp_info.exelinkflags.append("-framework AVFoundation")
            self.cpp_info.exelinkflags.append("-framework AppKit")
            self.cpp_info.exelinkflags.append("-framework CoreGraphics")
            self.cpp_info.exelinkflags.append("-framework CoreMedia")
            self.cpp_info.exelinkflags.append("-framework Foundation")
            self.cpp_info.exelinkflags.append("-framework OpenGL")
            self.cpp_info.exelinkflags.append("-framework QuartzCore")

    def get_video_filters(self):
        self.output.info("Extracting only video filters")
        video_patterns = ["vf);", "vsrc);", "vsink);", "avf);", "avsrc);"]
        content = tools.load("FFmpeg/libavfilter/allfilters.c")
        video_filters = []
        for line in content.splitlines():
            if any(p in line for p in video_patterns):
                parts = line.split(",")
                video_filters.append(parts[1].strip())
        return video_filters
