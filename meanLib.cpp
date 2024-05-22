#include <stdio.h>

extern "C" {
    __declspec(dllexport) void movingMean(double data[], int size, int k, double avgList[]) {
    int centerIndex = (k - 1) / 2;

    for (int i = 0; i < size; i++) {
        double sum = 0;
        avgList[i]=0;
        int x = 0;
        for (int j = -centerIndex; j <= centerIndex; j++) {
            int index = i + j;
            if (index >= 0 && index < size) {
                sum += data[index];
                x++;
            }
        }
        avgList[i] = sum / x;
    }
}
}




