//
// Created by Congyu Luo on 4/27/23.
//

#ifndef TEST_ALLOCTRACKER_H
#define TEST_ALLOCTRACKER_H

// Standard LL for tracking allocations

#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct allocNode {
    void *ptr;
    size_t size;
    bool isFreed;
    int id;
    struct allocNode *next;
} allocNode;

typedef struct allocList {
    allocNode *head;
    int size;
} allocList;

void addNode(allocNode *node);
allocNode* findAllocNode(void *ptr);
int freeAlloc(void *ptr);
void* addAlloc(void *ptr, size_t size);

// Dereference search functions
bool inRange(allocNode *node, void* ptr);
allocNode* getAllocatedNode(void* ptr);

void exportAllocList();

void deleteList();

// Print function
void printAllocList();
void printAllAllocList();

// Test func
allocNode* getAllocHead();

#endif //TEST_ALLOCTRACKER_H
