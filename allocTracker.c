//
// Created by Congyu Luo on 4/27/23.
//

#include "allocTracker.h"

// Declare allocList struct statically on stack
allocList aList = {NULL, 0};

void addNode(allocNode *node) {
    // Add node to the front of the list
    if (aList.head == NULL) {
        aList.head = node;
    } else {
        node->next = aList.head;
        aList.head = node;
    }
    // Increment size
    aList.size++;
}

void* addAlloc(void *ptr, size_t size) {
    // Allocate new node
    allocNode *node = (allocNode*) malloc(sizeof(allocNode));
    node->ptr = ptr;
    node->size = size;
    node->isFreed = false;
    node->id = aList.size;
    node->next = NULL;
    // Add node to list
    addNode(node);
    return node;
}

allocNode* findAllocNode(void *ptr) {
    allocNode *curr = aList.head;
    while (curr != NULL) {
        if (curr->ptr == ptr && !curr->isFreed) {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}

int freeAlloc(void *ptr) {
    allocNode *curr = aList.head;
    while (curr != NULL) {
        if (curr->ptr == ptr && !curr->isFreed) {
            // Mark as freed
            curr->isFreed = true;
            return 1;
        }
        curr = curr->next;
    }
    return 0;
}

bool inRange(allocNode *node, void* ptr) {
    return (node->ptr <= ptr && ptr < (char*) node->ptr + node->size);
}

allocNode* getAllocatedNode(void* ptr) {
    allocNode *curr = aList.head;
    while (curr != NULL && !curr->isFreed) {
        if (inRange(curr, ptr)) {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}

void exportAllocList() {
    allocNode *curr = aList.head;
    FILE *fp = fopen("allocTable.cymp", "w");
    if (fp == NULL) {
        fprintf(stderr, "Error opening file!\n");
        exit(1);
    }
    while (curr != NULL) {
        // Print range and size of each allocation
        fprintf(fp, "%d, %p, %zu, %d\n", curr->id, curr->ptr, curr->size, curr->isFreed);
        curr = curr->next;
    }
    fclose(fp);
}

void deleteList() {
    allocNode *curr = aList.head;
    allocNode *next = NULL;
    while (curr != NULL) {
        next = curr->next;
        free(curr);
        curr = next;
    }
    aList.head = NULL;
    aList.size = 0;
}

void printAllocList() {
    allocNode *curr = aList.head;
    int count = 0;
    while (curr != NULL) {
        if (!curr->isFreed) {
            // Print range and size of each allocation
            printf("%d: [%p - %p], size: [%zu]\n", curr->id, curr->ptr, curr->ptr + curr->size - 1, curr->size);
            count++;
        }
        curr = curr->next;
    }
    if (count == 0) {
        printf("List is empty\n");
    }
}

void printAllAllocList() {
    allocNode *curr = aList.head;
    int count = 0;
    while (curr != NULL) {
        if (!curr->isFreed) {
            // Print range and size of each allocation
            printf("%d: [%p - %p], size: [%zu]\n", curr->id, curr->ptr, curr->ptr + curr->size - 1, curr->size);
        } else {
            printf("%d: [%p - %p], size: [%zu] FREED\n", curr->id, curr->ptr, curr->ptr + curr->size - 1, curr->size);
        }
        curr = curr->next;
        count++;
    }
    if (count == 0) {
        printf("List is empty\n");
    }
}

allocNode* getAllocHead() {
    return aList.head;
}


