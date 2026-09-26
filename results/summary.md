# Results summary

## Change vs. Q8_0 on the same items (paired)

Negative = worse than Q8_0. *lost/gained*: items Q8_0 got right and this quant got wrong, and vice versa. p: exact McNemar test.

| model | quant | task | lang | Δ accuracy | paired 95% CI | lost / gained | p |
|---|---|---|---|---|---|---|---|
| gemma4-e4b | Q6_K | belebele | eng | +0.0 | -1.5 to +1.5 | 1 / 1 | 1.000 |
| gemma4-e4b | Q4_K_M | belebele | eng | -1.5 | -4.0 to +1.0 | 5 / 2 | 0.453 |
| gemma4-e4b | Q3_K_M | belebele | eng | -8.5 * | -13.0 to -4.0 | 21 / 4 | 0.001 |
| gemma4-e4b | Q2_K | belebele | eng | -73.5 * | -80.0 to -66.5 | 153 / 6 | 0.000 |
| gemma4-e4b | Q6_K | belebele | yor | -2.0 | -5.5 to +1.0 | 8 / 4 | 0.388 |
| gemma4-e4b | Q4_K_M | belebele | yor | -4.5 | -9.5 to +0.5 | 18 / 9 | 0.122 |
| gemma4-e4b | Q3_K_M | belebele | yor | -10.0 * | -18.0 to -2.0 | 46 / 26 | 0.024 |
| gemma4-e4b | Q2_K | belebele | yor | -20.0 * | -29.0 to -11.5 | 65 / 25 | 0.000 |
| gemma4-e4b | Q6_K | sentiment | eng | -1.0 | -2.5 to +0.0 | 2 / 0 | 0.500 |
| gemma4-e4b | Q4_K_M | sentiment | eng | +0.0 | -3.0 to +3.0 | 4 / 4 | 1.000 |
| gemma4-e4b | Q3_K_M | sentiment | eng | -0.5 | -5.0 to +4.0 | 12 / 11 | 1.000 |
| gemma4-e4b | Q2_K | sentiment | eng | -28.5 * | -37.5 to -19.5 | 76 / 19 | 0.000 |
| gemma4-e4b | Q6_K | sentiment | pcm | -1.5 | -4.0 to +0.5 | 4 / 1 | 0.375 |
| gemma4-e4b | Q4_K_M | sentiment | pcm | -5.5 | -11.0 to +0.0 | 21 / 10 | 0.071 |
| gemma4-e4b | Q3_K_M | sentiment | pcm | -8.5 * | -15.0 to -2.0 | 33 / 16 | 0.021 |
| gemma4-e4b | Q2_K | sentiment | pcm | -32.0 * | -42.0 to -22.5 | 95 / 31 | 0.000 |
| gemma4-e4b | Q6_K | sentiment | yor | +0.0 | -2.0 to +2.0 | 2 / 2 | 1.000 |
| gemma4-e4b | Q4_K_M | sentiment | yor | +4.5 | +0.5 to +9.0 | 5 / 14 | 0.064 |
| gemma4-e4b | Q3_K_M | sentiment | yor | +3.5 | -5.0 to +12.5 | 39 / 46 | 0.515 |
| gemma4-e4b | Q2_K | sentiment | yor | -13.0 * | -23.5 to -3.0 | 71 / 45 | 0.020 |
| qwen3.5-4b | Q6_K | belebele | eng | +0.5 | +0.0 to +1.5 | 0 / 1 | 1.000 |
| qwen3.5-4b | Q4_K_M | belebele | eng | -1.5 | -4.5 to +1.5 | 6 / 3 | 0.508 |
| qwen3.5-4b | Q3_K_M | belebele | eng | +1.0 | -2.5 to +4.5 | 5 / 7 | 0.774 |
| qwen3.5-4b | Q2_K | belebele | eng | -39.5 * | -47.0 to -32.0 | 84 / 5 | 0.000 |
| qwen3.5-4b | Q6_K | belebele | yor | +0.0 | -3.5 to +3.5 | 6 / 6 | 1.000 |
| qwen3.5-4b | Q4_K_M | belebele | yor | -1.0 | -6.0 to +4.5 | 15 / 13 | 0.851 |
| qwen3.5-4b | Q3_K_M | belebele | yor | -7.5 * | -14.5 to -1.0 | 31 / 16 | 0.040 |
| qwen3.5-4b | Q2_K | belebele | yor | -16.5 * | -26.0 to -7.0 | 61 / 28 | 0.001 |
| qwen3.5-4b | Q6_K | sentiment | eng | +0.5 | +0.0 to +1.5 | 0 / 1 | 1.000 |
| qwen3.5-4b | Q4_K_M | sentiment | eng | +1.0 | -3.0 to +4.5 | 7 / 9 | 0.804 |
| qwen3.5-4b | Q3_K_M | sentiment | eng | +0.0 | -4.0 to +3.5 | 8 / 8 | 1.000 |
| qwen3.5-4b | Q2_K | sentiment | eng | -21.5 * | -30.5 to -13.0 | 68 / 25 | 0.000 |
| qwen3.5-4b | Q6_K | sentiment | pcm | -0.5 | -2.5 to +1.5 | 3 / 2 | 1.000 |
| qwen3.5-4b | Q4_K_M | sentiment | pcm | +1.5 | -4.0 to +7.0 | 16 / 19 | 0.736 |
| qwen3.5-4b | Q3_K_M | sentiment | pcm | -1.0 | -8.0 to +6.0 | 24 / 22 | 0.883 |
| qwen3.5-4b | Q2_K | sentiment | pcm | -21.5 * | -31.0 to -12.0 | 71 / 28 | 0.000 |
| qwen3.5-4b | Q6_K | sentiment | yor | -0.5 | -3.5 to +2.5 | 5 / 4 | 1.000 |
| qwen3.5-4b | Q4_K_M | sentiment | yor | -6.5 * | -12.0 to -1.0 | 24 / 11 | 0.041 |
| qwen3.5-4b | Q3_K_M | sentiment | yor | -12.5 * | -21.0 to -4.0 | 52 / 27 | 0.007 |
| qwen3.5-4b | Q2_K | sentiment | yor | -22.5 * | -31.5 to -12.5 | 75 / 30 | 0.000 |

## Accuracy by config (95% CI)

| model | quant | task | lang | acc | 95% CI | % of Q8_0 | sentiment macro-F1 |
|---|---|---|---|---|---|---|---|
| gemma4-e4b | Q8_0 | belebele | eng | 93.5% | 90.0%–96.5% | 100.0% |  |
| gemma4-e4b | Q6_K | belebele | eng | 93.5% | 90.0%–96.5% | 100.0% |  |
| gemma4-e4b | Q4_K_M | belebele | eng | 92.0% | 88.0%–95.5% | 98.4% |  |
| gemma4-e4b | Q3_K_M | belebele | eng | 85.0% | 80.0%–89.5% | 90.9% |  |
| gemma4-e4b | Q2_K | belebele | eng | 20.0% | 14.5%–25.5% | 21.4% |  |
| gemma4-e4b | Q8_0 | belebele | yor | 41.5% | 35.0%–48.0% | 100.0% |  |
| gemma4-e4b | Q6_K | belebele | yor | 39.5% | 33.0%–46.5% | 95.2% |  |
| gemma4-e4b | Q4_K_M | belebele | yor | 37.0% | 30.5%–43.5% | 89.2% |  |
| gemma4-e4b | Q3_K_M | belebele | yor | 31.5% | 25.0%–38.0% | 75.9% |  |
| gemma4-e4b | Q2_K | belebele | yor | 21.5% | 16.0%–27.0% | 51.8% |  |
| gemma4-e4b | Q8_0 | sentiment | eng | 64.5% | 58.0%–71.0% | 100.0% | 0.628 |
| gemma4-e4b | Q6_K | sentiment | eng | 63.5% | 57.0%–70.0% | 98.4% | 0.620 |
| gemma4-e4b | Q4_K_M | sentiment | eng | 64.5% | 58.0%–71.0% | 100.0% | 0.621 |
| gemma4-e4b | Q3_K_M | sentiment | eng | 64.0% | 57.5%–71.0% | 99.2% | 0.582 |
| gemma4-e4b | Q2_K | sentiment | eng | 36.0% | 30.0%–43.0% | 55.8% | 0.356 |
| gemma4-e4b | Q8_0 | sentiment | pcm | 62.5% | 56.0%–69.0% | 100.0% | 0.614 |
| gemma4-e4b | Q6_K | sentiment | pcm | 61.0% | 54.5%–67.5% | 97.6% | 0.601 |
| gemma4-e4b | Q4_K_M | sentiment | pcm | 57.0% | 50.5%–64.0% | 91.2% | 0.558 |
| gemma4-e4b | Q3_K_M | sentiment | pcm | 54.0% | 47.0%–61.0% | 86.4% | 0.514 |
| gemma4-e4b | Q2_K | sentiment | pcm | 30.5% | 24.0%–37.0% | 48.8% | 0.305 |
| gemma4-e4b | Q8_0 | sentiment | yor | 54.0% | 47.0%–61.0% | 100.0% | 0.528 |
| gemma4-e4b | Q6_K | sentiment | yor | 54.0% | 47.0%–61.0% | 100.0% | 0.526 |
| gemma4-e4b | Q4_K_M | sentiment | yor | 58.5% | 51.5%–65.5% | 108.3% | 0.581 |
| gemma4-e4b | Q3_K_M | sentiment | yor | 57.5% | 51.0%–64.5% | 106.5% | 0.557 |
| gemma4-e4b | Q2_K | sentiment | yor | 41.0% | 34.5%–47.5% | 75.9% | 0.390 |
| qwen3.5-4b | Q8_0 | belebele | eng | 91.5% | 87.5%–95.0% | 100.0% |  |
| qwen3.5-4b | Q6_K | belebele | eng | 92.0% | 88.0%–95.5% | 100.5% |  |
| qwen3.5-4b | Q4_K_M | belebele | eng | 90.0% | 85.5%–94.0% | 98.4% |  |
| qwen3.5-4b | Q3_K_M | belebele | eng | 92.5% | 89.0%–96.0% | 101.1% |  |
| qwen3.5-4b | Q2_K | belebele | eng | 52.0% | 45.5%–58.5% | 56.8% |  |
| qwen3.5-4b | Q8_0 | belebele | yor | 44.5% | 37.5%–51.5% | 100.0% |  |
| qwen3.5-4b | Q6_K | belebele | yor | 44.5% | 37.5%–51.5% | 100.0% |  |
| qwen3.5-4b | Q4_K_M | belebele | yor | 43.5% | 36.5%–50.0% | 97.8% |  |
| qwen3.5-4b | Q3_K_M | belebele | yor | 37.0% | 30.5%–44.0% | 83.1% |  |
| qwen3.5-4b | Q2_K | belebele | yor | 28.0% | 22.0%–34.0% | 62.9% |  |
| qwen3.5-4b | Q8_0 | sentiment | eng | 66.5% | 60.5%–73.0% | 100.0% | 0.644 |
| qwen3.5-4b | Q6_K | sentiment | eng | 67.0% | 60.5%–73.5% | 100.8% | 0.651 |
| qwen3.5-4b | Q4_K_M | sentiment | eng | 67.5% | 61.0%–74.0% | 101.5% | 0.668 |
| qwen3.5-4b | Q3_K_M | sentiment | eng | 66.5% | 60.0%–73.0% | 100.0% | 0.650 |
| qwen3.5-4b | Q2_K | sentiment | eng | 45.0% | 38.5%–52.0% | 67.7% | 0.451 |
| qwen3.5-4b | Q8_0 | sentiment | pcm | 57.5% | 51.0%–64.5% | 100.0% | 0.566 |
| qwen3.5-4b | Q6_K | sentiment | pcm | 57.0% | 50.0%–64.0% | 99.1% | 0.561 |
| qwen3.5-4b | Q4_K_M | sentiment | pcm | 59.0% | 52.0%–65.5% | 102.6% | 0.584 |
| qwen3.5-4b | Q3_K_M | sentiment | pcm | 56.5% | 49.5%–63.5% | 98.3% | 0.565 |
| qwen3.5-4b | Q2_K | sentiment | pcm | 36.0% | 29.5%–43.0% | 62.6% | 0.326 |
| qwen3.5-4b | Q8_0 | sentiment | yor | 58.5% | 51.5%–65.0% | 100.0% | 0.585 |
| qwen3.5-4b | Q6_K | sentiment | yor | 58.0% | 51.0%–65.0% | 99.1% | 0.580 |
| qwen3.5-4b | Q4_K_M | sentiment | yor | 52.0% | 45.0%–59.0% | 88.9% | 0.512 |
| qwen3.5-4b | Q3_K_M | sentiment | yor | 46.0% | 38.5%–53.0% | 78.6% | 0.425 |
| qwen3.5-4b | Q2_K | sentiment | yor | 36.0% | 29.0%–42.5% | 61.5% | 0.305 |

## Token tax: average prompt length for the same content

| model | task | lang | avg prompt tokens | × English |
|---|---|---|---|---|
| gemma4-e4b | belebele | eng | 190 | 1.00× |
| gemma4-e4b | belebele | yor | 357 | 1.88× |
| gemma4-e4b | sentiment | eng | 66 | 1.00× |
| gemma4-e4b | sentiment | pcm | 63 | 0.96× |
| gemma4-e4b | sentiment | yor | 86 | 1.31× |
| qwen3.5-4b | belebele | eng | 195 | 1.00× |
| qwen3.5-4b | belebele | yor | 394 | 2.02× |
| qwen3.5-4b | sentiment | eng | 70 | 1.00× |
| qwen3.5-4b | sentiment | pcm | 67 | 0.96× |
| qwen3.5-4b | sentiment | yor | 95 | 1.36× |

## Memory

| model | quant | file GB | GPU weights MiB | GPU KV MiB (16k ctx) | GPU total MiB |
|---|---|---|---|---|---|
| gemma4-e4b | Q8_0 | 8.031 | 7644 | 416 | 8254 |
| gemma4-e4b | Q6_K | 6.217 | 5914 | 416 | 6524 |
| gemma4-e4b | Q4_K_M | 5.335 | 5073 | 416 | 5683 |
| gemma4-e4b | Q3_K_M | 4.85 | 4611 | 416 | 5221 |
| gemma4-e4b | Q2_K | 4.401 | 4182 | 416 | 4793 |
| qwen3.5-4b | Q8_0 | 4.622 | 4275 | 512 | 4981 |
| qwen3.5-4b | Q6_K | 3.563 | 3293 | 512 | 3999 |
| qwen3.5-4b | Q4_K_M | 2.783 | 2573 | 512 | 3279 |
| qwen3.5-4b | Q3_K_M | 2.319 | 2147 | 512 | 2853 |
| qwen3.5-4b | Q2_K | 1.959 | 1816 | 512 | 2522 |

## Speed (llama-bench, median of 5)

| model | quant | test | context depth | tok/s | ± |
|---|---|---|---|---|---|
| gemma4-e4b | Q8_0 | pp512 | 0 | 370.9 | 6.3 |
| gemma4-e4b | Q8_0 | pp512 | 4096 | 326.6 | 0.7 |
| gemma4-e4b | Q8_0 | tg128 | 0 | 19.7 | 0.2 |
| gemma4-e4b | Q8_0 | tg128 | 4096 | 18.9 | 0.3 |
| gemma4-e4b | Q6_K | pp512 | 0 | 328.4 | 20.6 |
| gemma4-e4b | Q6_K | pp512 | 4096 | 309.4 | 0.9 |
| gemma4-e4b | Q6_K | tg128 | 0 | 23.3 | 0.1 |
| gemma4-e4b | Q6_K | tg128 | 4096 | 23.0 | 0.0 |
| gemma4-e4b | Q4_K_M | pp512 | 0 | 345.1 | 13.6 |
| gemma4-e4b | Q4_K_M | pp512 | 4096 | 305.5 | 8.6 |
| gemma4-e4b | Q4_K_M | tg128 | 0 | 28.6 | 1.0 |
| gemma4-e4b | Q4_K_M | tg128 | 4096 | 27.6 | 0.6 |
| gemma4-e4b | Q3_K_M | pp512 | 0 | 330.2 | 7.3 |
| gemma4-e4b | Q3_K_M | pp512 | 4096 | 296.7 | 1.7 |
| gemma4-e4b | Q3_K_M | tg128 | 0 | 24.4 | 0.3 |
| gemma4-e4b | Q3_K_M | tg128 | 4096 | 23.4 | 0.2 |
| gemma4-e4b | Q2_K | pp512 | 0 | 340.7 | 8.8 |
| gemma4-e4b | Q2_K | pp512 | 4096 | 278.8 | 0.9 |
| gemma4-e4b | Q2_K | tg128 | 0 | 26.0 | 2.1 |
| gemma4-e4b | Q2_K | tg128 | 4096 | 25.9 | 1.0 |
| qwen3.5-4b | Q8_0 | pp512 | 0 | 309.6 | 10.5 |
| qwen3.5-4b | Q8_0 | pp512 | 4096 | 316.0 | 1.6 |
| qwen3.5-4b | Q8_0 | tg128 | 0 | 17.8 | 0.2 |
| qwen3.5-4b | Q8_0 | tg128 | 4096 | 17.5 | 0.2 |
| qwen3.5-4b | Q6_K | pp512 | 0 | 332.3 | 3.8 |
| qwen3.5-4b | Q6_K | pp512 | 4096 | 304.8 | 0.6 |
| qwen3.5-4b | Q6_K | tg128 | 0 | 22.3 | 0.1 |
| qwen3.5-4b | Q6_K | tg128 | 4096 | 21.5 | 0.1 |
| qwen3.5-4b | Q4_K_M | pp512 | 0 | 341.3 | 2.1 |
| qwen3.5-4b | Q4_K_M | pp512 | 4096 | 311.7 | 0.4 |
| qwen3.5-4b | Q4_K_M | tg128 | 0 | 27.8 | 0.2 |
| qwen3.5-4b | Q4_K_M | tg128 | 4096 | 26.5 | 0.1 |
| qwen3.5-4b | Q3_K_M | pp512 | 0 | 327.1 | 3.9 |
| qwen3.5-4b | Q3_K_M | pp512 | 4096 | 281.0 | 7.9 |
| qwen3.5-4b | Q3_K_M | tg128 | 0 | 26.8 | 0.9 |
| qwen3.5-4b | Q3_K_M | tg128 | 4096 | 24.8 | 0.1 |
| qwen3.5-4b | Q2_K | pp512 | 0 | 325.3 | 1.7 |
| qwen3.5-4b | Q2_K | pp512 | 4096 | 294.4 | 0.7 |
| qwen3.5-4b | Q2_K | tg128 | 0 | 32.0 | 0.1 |
| qwen3.5-4b | Q2_K | tg128 | 4096 | 30.0 | 0.0 |
