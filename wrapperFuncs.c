//
// Created by Congyu Luo on 4/28/23.
//

#include "wrapperFuncs.h"
#include "allocTracker.h"
#include "runtimeTracker.h"

void* logAccess(void* ptr, int id) {
    // Check if accessing an allocated location
    allocNode* allocBlock = getAllocatedNode(ptr);
    if (allocBlock != NULL) {
        // Add to runtime list
        logRuntimeDeref(DEREFERENCE, id, allocBlock);
    } // To add more func later, external access.
    return ptr;
}

void logScopeEnter(int id) {
    // Add to runtime list
    logRuntimeGeneral(SCOPE_ENTER, id);
}

void logScopeExit(int id) {
    // Add to runtime list
    logRuntimeGeneral(SCOPE_EXIT, id);
}

void logReturn(){
    // Add to runtime list
    logRuntimeGeneral(RETURN, -1);
}

int logExtParam(void* param, int id) {
    // Check if accessing an allocated location
    allocNode* allocBlock = getAllocatedNode(param);
    if (allocBlock != NULL) {
        // Add to runtime list
        logRuntimeDeref(EXT_PARAM, id, allocBlock);
    } // To add more func later, external access.
    return 0;
}

void* mallocWrapper(size_t size) {
    void* ptr = malloc(size);
    if (ptr == NULL) {
        // Print error message
        fprintf(stderr, "mallocWrapper: Memory allocation failed.\n");
        return NULL;
    }
    // Add to alloc list
    allocNode* newAlloc = addAlloc(ptr, size);
    // Add to runtime list
    logRuntimeAlloc(MALLOC, -1, newAlloc);
    return ptr;
}

void* callocWrapper(size_t num, size_t size) {
    void* ptr = calloc(num, size);
    if (ptr == NULL) {
        // Print error message
        fprintf(stderr, "callocWrapper: Memory allocation failed.\n");
        return NULL;
    }
    allocNode* newAlloc = addAlloc(ptr, size*num);
    // Add to runtime list
    logRuntimeAlloc(CALLOC, -1, newAlloc);
    return ptr;
}

void* vallocWrapper(size_t size) {
    void* ptr = valloc(size);
    if (ptr == NULL) {
        // Print error message
        fprintf(stderr, "vallocWrapper: Memory allocation failed.\n");
        return NULL;
    }
    allocNode* newAlloc = addAlloc(ptr, size);
    // Add to runtime list
    logRuntimeAlloc(VALLOC, -1, newAlloc);
    return ptr;
}

void* aligned_allocWrapper(size_t alignment, size_t size) {
    void* ptr = aligned_alloc(alignment, size);
    if (ptr == NULL) {
        // Print error message
        fprintf(stderr, "aligned_allocWrapper: Memory allocation failed.\n");
        return NULL;
    }
    allocNode* newAlloc = addAlloc(ptr, size);
    // Add to runtime list
    logRuntimeAlloc(ALIGNED_ALLOC, -1, newAlloc);
    return ptr;
}

void* reallocWrapper(void* ptr, size_t size) {
    // Call realloc
    void* reallocPtr = realloc(ptr, size);
    if (reallocPtr == NULL) { // Reallocation failed
        // Print error message
        fprintf(stderr, "reallocWrapper: Memory reallocation failed.\n");
        return NULL;
    }
    // Get pointer for ptr's allocNode
    allocNode* alloc = findAllocNode(ptr);
    if (alloc == NULL) {
        // Print error message
        fprintf(stderr, "reallocWrapper: Address being reallocated not found in allocList.\n");
        return NULL;
    }
    // Remove original ptr from list
    freeAlloc(ptr);
    // Add new ptr to list
    allocNode* newAlloc = addAlloc(reallocPtr, size);
    // Add to runtime list
    logRuntimeRealloc(REALLOC, -1, newAlloc, alloc);
    return reallocPtr;
}

void atExitFunc() {
    // Add to runtime list
    logRuntimeGeneral(EXIT, -1);

    // Export runtimeList to file
    exportRuntimeList();
    // Export allocTable to file
    exportAllocList();

    // Print runtimeList
    printf("\nRuntime List:\n");
    printRuntimeList();
    // Print allocList
    printf("\nAlloc List:\n");
    printAllAllocList();

    // Delete the allocList
    deleteList();
    // Delete the runtimeList
    deleteRuntimeList();
}

void freeWrapper(void* ptr) {
    // Free the memory
    free(ptr);
    // Find the allocNode
    allocNode* alloc = findAllocNode(ptr);
    if (alloc == NULL) {
        // Print error message
        fprintf(stderr, "freeWrapper: Address being freed not found in allocList.\n");
        return;
    }
    // Remove node from list
    freeAlloc(ptr);
    // Add to runtime list
    logRuntimeFree(FREE, -1, alloc);
}