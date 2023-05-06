


typedef struct {
    int x;
    int y;
} Point;

void print_point(Point *p) {
logScopeEnter(0);

    printf("Point: (%d, %d)\n", p->x, p->y);

logScopeExit(0);
}

void initialize_point(Point *p, int x, int y) {
logScopeEnter(1);

    p->x = x;
    p->y = y;

logScopeExit(1);
}

void modify_point(Point *p, int dx, int dy) {
logScopeEnter(2);

    p->x += dx;
    p->y += dy;

logScopeExit(2);
}

int *initialize_array(int size) {
logScopeEnter(3);

    int *arr = (int *)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
logScopeEnter(4);

        arr[i] = i;
    
logScopeExit(4);
}
    
logReturn();
return arr;

logScopeExit(3);
}

void print_array(int *arr, int size) {
logScopeEnter(5);

    printf("Array: ");
    for (int i = 0; i < size; i++) {
logScopeEnter(6);

        printf("%d ", arr[i]);
    
logScopeExit(6);
}
    printf("\n");

logScopeExit(5);
}

int main() {
logScopeEnter(7);

    
    int *arr = initialize_array(5);

    
    print_array(arr, 5);

    
    arr = (int *)realloc(arr, 10 * sizeof(int));

    
    for (int i = 5; i < 10; i++) {
logScopeEnter(8);

        arr[i] = i;
    
logScopeExit(8);
}

    
    print_array(arr, 10);

    
    Point *p = (Point *)malloc(sizeof(Point));

    
    initialize_point(p, 10, 20);

    
    print_point(p);

    
    modify_point(p, 5, -10);

    
    print_point(p);

    
    free(arr);
    free(p);

    
logReturn();
return 0;

logScopeExit(7);
}
