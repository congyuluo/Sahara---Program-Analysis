//
// Created by Congyu Luo on 5/4/23.
//

#ifndef TEST_RUNTIMETRACKER_H
#define TEST_RUNTIMETRACKER_H

#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "allocTracker.h"

// Enum for runtime action types
enum runtimeActionType {
    DEREFERENCE, // Pointer dereference at runtime
    SCOPE_ENTER, // Scope enter
    SCOPE_EXIT,  // Scope exit
    RETURN,      // Return
    EXT_PARAM,   // External parameter
    FREE,        // Free
    MALLOC,      // Malloc
    CALLOC,      // Calloc
    VALLOC,      // Valloc
    ALIGNED_ALLOC, // Aligned Alloc
    REALLOC,     // Realloc
    EXIT         // Program Exit
};

// LL for tracking runtime
typedef struct runtimeNode {
    int id;
    enum runtimeActionType type;
    struct timespec time;
    struct runtimeNode *next;
    // For allocation & dereference actions, pointer to aList node.
    allocNode* alocNode;
    // For Free / realloc actions, pointer to the old aList node.
    allocNode* freedAllocNode;
} runtimeNode;

typedef struct runtimeList {
    runtimeNode *head;
    runtimeNode *tail;
    int size;
} runtimeList;

// Helper functions for determining node action types
bool isAllocAction(enum runtimeActionType type);
bool isReallocAction(enum runtimeActionType type);
bool isDerefAction(enum runtimeActionType type);
bool isFreeAction(enum runtimeActionType type);

void addRuntimeNode(runtimeNode *node);
runtimeNode* basicRuntimeNode(enum runtimeActionType type, int id);
void logRuntimeGeneral(enum runtimeActionType type, int id);
void logRuntimeAlloc(enum runtimeActionType type, int id, allocNode* newAlloc);
void logRuntimeRealloc(enum runtimeActionType type, int id, allocNode* newAlloc, allocNode* oldAlloc);
void logRuntimeDeref(enum runtimeActionType type, int id, allocNode* alloc);
void logRuntimeFree(enum runtimeActionType type, int id, allocNode* alloc);


void deleteRuntimeList();

void printRuntimeList();

void exportRuntimeList();

#endif //TEST_RUNTIMETRACKER_H
