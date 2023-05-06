//
// Created by Congyu Luo on 5/4/23.
//

#include "runtimeTracker.h"

// Runtime logging functions
runtimeList rList = {NULL, NULL, 0};

bool isAllocAction(enum runtimeActionType type) {
    return type == MALLOC || type == CALLOC || type == VALLOC || type == ALIGNED_ALLOC;
}

bool isReallocAction(enum runtimeActionType type) {
    return type == REALLOC;
}

bool isDerefAction(enum runtimeActionType type) {
    return type == DEREFERENCE || type == EXT_PARAM;
}

bool isFreeAction(enum runtimeActionType type) {
    return type == FREE;
}

void addRuntimeNode(runtimeNode *node) {
    if (rList.head == NULL) {
        rList.head = node;
        rList.tail = node;
    } else {
        // Add node to the end of the list
        rList.tail->next = node;
        rList.tail = node;
    }
    // Increment size
    rList.size++;
}

runtimeNode* basicRuntimeNode(enum runtimeActionType type, int id) {
    // Allocate new node
    runtimeNode *node = (runtimeNode *) malloc(sizeof(runtimeNode));
    node->id = id;
    node->type = type;
    if (clock_gettime(CLOCK_REALTIME, &node->time) != 0) {
        fprintf(stderr, "Error getting time\n");
        exit(1);
    }
    node->next = NULL;
    node->alocNode = NULL;
    node->freedAllocNode = NULL;
    return node;
}

void logRuntimeGeneral(enum runtimeActionType type, int id) {
    runtimeNode *node = basicRuntimeNode(type, id);
    // Add node to list
    addRuntimeNode(node);
}

void logRuntimeAlloc(enum runtimeActionType type, int id, allocNode* newAlloc) {
    runtimeNode *node = basicRuntimeNode(type, id);
    node->alocNode = newAlloc;
    // Add node to list
    addRuntimeNode(node);
}

void logRuntimeRealloc(enum runtimeActionType type, int id, allocNode* newAlloc, allocNode* oldAlloc) {
    runtimeNode *node = basicRuntimeNode(type, id);
    node->alocNode = newAlloc;
    node->freedAllocNode = oldAlloc;
    // Add node to list
    addRuntimeNode(node);
}

void logRuntimeDeref(enum runtimeActionType type, int id, allocNode* alloc) {
    runtimeNode *node = basicRuntimeNode(type, id);
    node->alocNode = alloc;
    // Add node to list
    addRuntimeNode(node);
}

void logRuntimeFree(enum runtimeActionType type, int id, allocNode* alloc) {
    runtimeNode *node = basicRuntimeNode(type, id);
    node->freedAllocNode = alloc;
    // Add node to list
    addRuntimeNode(node);
}

void deleteRuntimeList() {
    runtimeNode *curr = rList.head;
    runtimeNode *next = NULL;
    while (curr != NULL) {
        next = curr->next;
        free(curr);
        curr = next;
    }
    rList.head = NULL;
    rList.tail = NULL;
    rList.size = 0;
}

void printRuntimeList() {
    runtimeNode *curr = rList.head;
    if (curr == NULL) {
        printf("List is empty\n");
        return;
    }
    int count = 0;
    while (curr != NULL) {
        printf("%d: ", count);
        if (isAllocAction(curr->type)) {
            switch (curr->type) {
                case MALLOC:
                    printf("MALLOC");
                    break;
                case CALLOC:
                    printf("CALLOC");
                    break;
                case VALLOC:
                    printf("VALLOC");
                    break;
                case ALIGNED_ALLOC:
                    printf("ALIGNED_ALLOC");
                    break;
            }
            allocNode* a_Node = curr->alocNode;
            printf(" [id: %d, time: %ld.%09ld] ([%p - %p], size: [%zu])\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, a_Node->ptr, a_Node->ptr + a_Node->size - 1, a_Node->size);
        } else if (isReallocAction(curr->type)) {
            allocNode* a_Node = curr->alocNode;
            allocNode* f_Node = curr->freedAllocNode;
            printf("REALLOC [id: %d, time: %ld.%09ld] ([%p - %p], size: [%zu]) -> ([%p - %p], size: [%zu])\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, f_Node->ptr, f_Node->ptr + f_Node->size - 1, f_Node->size, a_Node->ptr, a_Node->ptr + a_Node->size - 1, a_Node->size);
        } else if (isDerefAction(curr->type)) {
            switch (curr->type) {
                case DEREFERENCE:
                    printf("DEREFERENCE");
                    break;
                case EXT_PARAM:
                    printf("EXT_PARAM");
                    break;
            }
            allocNode* a_Node = curr->alocNode;
            printf(" [id: %d, time: %ld.%09ld] ([%p - %p], size: [%zu])\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, a_Node->ptr, a_Node->ptr + a_Node->size - 1, a_Node->size);
        } else if (isFreeAction(curr->type)) {
            allocNode* f_Node = curr->freedAllocNode;
            printf("FREE [id: %d, time: %ld.%09ld] ([%p - %p], size: [%zu])\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, f_Node->ptr, f_Node->ptr + f_Node->size - 1, f_Node->size);
        } else { // General action
            switch (curr->type) {
                case SCOPE_ENTER:
                    printf("SCOPE_ENTER");
                    break;
                case SCOPE_EXIT:
                    printf("SCOPE_EXIT");
                    break;
                case RETURN:
                    printf("RETURN");
                    break;
                case EXIT:
                    printf("EXIT");
                    break;
            }
            printf(" [id: %d, time: %ld.%09ld]\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec);
        }
        curr = curr->next;
        count++;
    }
}

void exportRuntimeList() {
    const char *filename = "runtime.cymp";
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        fprintf(stderr, "Error opening file %s\n", filename);
        exit(1);
    }
    runtimeNode *curr = rList.head;
    while (curr != NULL) {
        if (isAllocAction(curr->type)) {
            switch (curr->type) {
                case MALLOC:
                    fprintf(fp, "MLOC");
                    break;
                case CALLOC:
                    fprintf(fp, "CLOC");
                    break;
                case VALLOC:
                    fprintf(fp, "VLOC");
                    break;
                case ALIGNED_ALLOC:
                    fprintf(fp, "ALOC");
                    break;
            }
            allocNode* a_Node = curr->alocNode;
            fprintf(fp, ", %d, %ld.%09ld, %d\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, a_Node->id);
        } else if (isReallocAction(curr->type)) {
            allocNode* a_Node = curr->alocNode;
            allocNode* f_Node = curr->freedAllocNode;
            fprintf(fp, "REAL, %d, %ld.%09ld, %d, %d\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, f_Node->id, a_Node->id);
        } else if (isDerefAction(curr->type)) {
            switch (curr->type) {
                case DEREFERENCE:
                    fprintf(fp, "DREF");
                    break;
                case EXT_PARAM:
                    fprintf(fp, "PRAM");
                    break;
            }
            allocNode* a_Node = curr->alocNode;
            fprintf(fp, ", %d, %ld.%09ld, %d\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, a_Node->id);
        } else if (isFreeAction(curr->type)) {
            allocNode* f_Node = curr->freedAllocNode;
            fprintf(fp, "FREE, %d, %ld.%09ld, %d\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec, f_Node->id);
        } else { // General action
            switch (curr->type) {
                case SCOPE_ENTER:
                    fprintf(fp, "SENT");
                    break;
                case SCOPE_EXIT:
                    fprintf(fp, "SEXT");
                    break;
                case RETURN:
                    fprintf(fp, "RETN");
                    break;
                case EXIT:
                    fprintf(fp, "EXIT");
                    break;
            }
            fprintf(fp, ", %d, %ld.%09ld\n", curr->id, curr->time.tv_sec, curr->time.tv_nsec);
        }
        curr = curr->next;
    }
    fclose(fp);
}