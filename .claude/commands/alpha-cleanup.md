# Alpha Cleanup Command

Perform mandatory workspace cleanup per alpha mode protocols.

## Steps

1. List all files in current directory
2. Identify test files (test_*.*, *_test.*)
3. Identify temporary files (*.tmp, *.log)
4. Remove all identified files
5. Verify workspace is clean
6. Report cleanup status

## Usage

Type `/alpha-cleanup` to execute mandatory workspace cleanup.