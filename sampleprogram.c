// C program to turn an
// image by 90 Degree
#include <stdio.h>
#include <stdlib.h>
void rotate(unsigned int *pS,
            unsigned int *pD,
            unsigned int row,
            unsigned int col);

void rotate(unsigned int *pS,
            unsigned int *pD,
            unsigned int row,
            unsigned int col)
{
    unsigned int r, c;
    for (r = 0; r < row; r++)
    {
        for (c = 0; c < col; c++)
        {
            *(pD + c * row + (row - r - 1)) =
                    *(pS + r * col + c);
        }
    }
}

void test_rotate(int m, int n) {
    // declarations
    unsigned int image[m][n];
    unsigned int *pSource;
    unsigned int *pDestination;
    int counter = 0;
    for (int i=0; i<m; i++){
        for (int j=0; j<n; j++){
            image[i][j] = counter;
            counter += 1;
        }
    }
    // setting initial values
    // and memory allocation
    pSource = (unsigned int *)image;
    pDestination =
            (unsigned int *)malloc
                    (sizeof(int) * m * n);
    // process each buffer
    rotate(pSource, pDestination, m, n);
    free(pDestination);
}
int main()
{
    for (int i=0; i<1000; i++){
        test_rotate(1000, 1000);
    }
    return 0;
}