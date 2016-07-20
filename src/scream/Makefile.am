AM_CPPFLAGS = $(CXX11_FLAGS) -I../sourdough -I../../third_party/scream/code
AM_CPPFLAGS += $(GLIB_CFLAGS)
AM_CXXFLAGS = $(PICKY_CXXFLAGS)

LDADD = ../sourdough/libsourdough.a -lpthread
LDADD += $(GLIB_LIBS)

bin_PROGRAMS = ScreamClient ScreamServer

ScreamClient_SOURCES = \
		ScreamClient.cc Packet.hh Packet.cc Timerfd.hh Timerfd.cc \
		../../third_party/scream/code/ScreamTx.h \
		../../third_party/scream/code/ScreamTx.cpp \
		../../third_party/scream/code/RtpQueue.h \
		../../third_party/scream/code/RtpQueue.cpp \
		../../third_party/scream/code/VideoEnc.h \
		../../third_party/scream/code/VideoEnc.cpp

ScreamServer_SOURCES = \
		ScreamServer.cc Packet.hh Packet.cc Timerfd.hh Timerfd.cc \
		../../third_party/scream/code/ScreamRx.h \
		../../third_party/scream/code/ScreamRx.cpp
