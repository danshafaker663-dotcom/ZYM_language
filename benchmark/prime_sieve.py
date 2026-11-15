"""Python reference implementation for the ZYM prime-sieve benchmark."""

import sys


def prime_sieve(limit: int) -> tuple[int, int]:
    is_prime = [True] * (limit + 1)
    if limit >= 0:
        is_prime[0] = False
    if limit >= 1:
        is_prime[1] = False

    candidate = 2
    while candidate * candidate <= limit:
        if is_prime[candidate]:
            multiple = candidate * candidate
            while multiple <= limit:
                is_prime[multiple] = False
                multiple += candidate
        candidate += 1

    prime_count = 0
    prime_sum = 0
    for number in range(2, limit + 1):
        if is_prime[number]:
            prime_count += 1
            prime_sum += number
    return prime_count, prime_sum


def main() -> int:
    line = sys.stdin.readline()
    if line == "":
        print("missing limit", file=sys.stderr)
        return 1
    prime_count, prime_sum = prime_sieve(int(line))
    print(prime_count)
    print(prime_sum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
