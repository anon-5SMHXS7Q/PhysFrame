#define CPPCHECK_MAJOR 1
#define CPPCHECK_MINOR 80
#define CPPCHECK_DEVMINOR 80

#define STRINGIFY(x) STRING(x)
#define STRING(VER) #VER
#if CPPCHECK_MINOR == CPPCHECK_DEVMINOR
#define CPPCHECK_VERSION_STRING STRINGIFY(CPPCHECK_MAJOR) "." STRINGIFY(CPPCHECK_DEVMINOR)
#define CPPCHECK_VERSION CPPCHECK_MAJOR,CPPCHECK_MINOR,0,0
#else
#define CPPCHECK_VERSION_STRING STRINGIFY(CPPCHECK_MAJOR) "." STRINGIFY(CPPCHECK_DEVMINOR) " dev"
#define CPPCHECK_VERSION CPPCHECK_MAJOR,CPPCHECK_MINOR,99,0
#endif
#define LEGALCOPYRIGHT L"Copyright (C) 2007-2017 Cppcheck team."
