#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int x;
    int y;
} Point;

void print_point(Point *p) {
    printf("Point: (%d, %d)\n", p->x, p->y);
}

void initialize_point(Point *p, int x, int y) {
    p->x = x;
    p->y = y;
}

void modify_point(Point *p, int dx, int dy) {
    p->x += dx;
    p->y += dy;
}

int *initialize_array(int size) {
    int *arr = (int *)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        arr[i] = i;
    }
    return arr;
}

void print_array(int *arr, int size) {
    printf("Array: ");
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main() {
    // Create and initialize an array using a function
    int *arr = initialize_array(5);

    // Print the array
    print_array(arr, 5);

    // Reallocate memory for the array
    arr = (int *)realloc(arr, 10 * sizeof(int));

    // Initialize the new elements
    for (int i = 5; i < 10; i++) {
        arr[i] = i;
    }

    // Print the updated array
    print_array(arr, 10);

    // Allocate memory for a Point struct
    Point *p = (Point *)malloc(sizeof(Point));

    // Initialize the Point struct using a function
    initialize_point(p, 10, 20);

    // Print the Point struct using a function
    print_point(p);

    // Modify the Point struct using a function
    modify_point(p, 5, -10);

    // Print the modified Point struct
    print_point(p);

    // Free allocated memory
    free(arr);
    free(p);

    return 0;
}
