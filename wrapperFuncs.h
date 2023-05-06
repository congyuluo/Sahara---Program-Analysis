//
// Created by Congyu Luo on 4/28/23.
//

#ifndef TEST_WRAPPERFUNCS_H
#define TEST_WRAPPERFUNCS_H

#include <stdlib.h>
// Runtime logging functions
void* logAccess(void* ptr, int id);
void logScopeEnter(int id);
void logScopeExit(int id);
void logReturn();

int logExtParam(void* param, int id);

void* mallocWrapper(size_t size);
void* callocWrapper(size_t num, size_t size);
void* vallocWrapper(size_t size);
void* aligned_allocWrapper(size_t alignment, size_t size);

void* reallocWrapper(void* ptr, size_t size);

void atExitFunc();

void freeWrapper(void* ptr);

#endif //TEST_WRAPPERFUNCS_H
