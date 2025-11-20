/**
 * @file buffered_file_reader.c
 * @brief Demonstrates buffered file I/O with comprehensive error handling
 * @note Follows MISRA C naming conventions
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>

/* Buffer size for file reading operations */
#define BUFFER_SIZE 1024U

/* Return codes */
#define EXIT_SUCCESS_CODE 0
#define EXIT_FAILURE_CODE 1

/**
 * @brief Reads a file using buffered I/O with error handling
 * @param file_path Pointer to the file path string
 * @return true if file read successfully, false otherwise
 */
static bool read_file_buffered(const char *file_path);

/**
 * @brief Displays usage information
 * @param program_name Name of the program executable
 */
static void display_usage(const char *program_name);

/**
 * @brief Main entry point
 * @param argc Argument count
 * @param argv Argument vector
 * @return EXIT_SUCCESS_CODE on success, EXIT_FAILURE_CODE on failure
 */
int main(int argc, char *argv[])
{
    int return_code = EXIT_SUCCESS_CODE;

    if (argc != 2)
    {
        display_usage(argv[0]);
        return_code = EXIT_FAILURE_CODE;
    }
    else
    {
        const char *file_path = argv[1];

        if (file_path == NULL)
        {
            fprintf(stderr, "Error: NULL file path provided\n");
            return_code = EXIT_FAILURE_CODE;
        }
        else
        {
            bool read_success = read_file_buffered(file_path);

            if (!read_success)
            {
                return_code = EXIT_FAILURE_CODE;
            }
        }
    }

    return return_code;
}

static bool read_file_buffered(const char *file_path)
{
    FILE *file_handle = NULL;
    char read_buffer[BUFFER_SIZE];
    size_t bytes_read = 0U;
    size_t total_bytes_read = 0U;
    bool operation_success = true;

    /* Validate input parameter */
    if (file_path == NULL)
    {
        fprintf(stderr, "Error: NULL file path provided to read_file_buffered\n");
        operation_success = false;
    }
    else
    {
        /* Open file for reading in binary mode */
        file_handle = fopen(file_path, "rb");

        if (file_handle == NULL)
        {
            fprintf(stderr, "Error: Failed to open file '%s': %s\n",
                    file_path, strerror(errno));
            operation_success = false;
        }
        else
        {
            printf("Successfully opened file: %s\n", file_path);
            printf("Reading file contents:\n");
            printf("-----------------------------------\n");

            /* Read file in chunks using buffered I/O */
            while (!feof(file_handle) && operation_success)
            {
                /* Clear buffer before reading */
                memset(read_buffer, 0, BUFFER_SIZE);

                /* Read data from file */
                bytes_read = fread(read_buffer, 1U, BUFFER_SIZE - 1U, file_handle);

                if (bytes_read > 0U)
                {
                    total_bytes_read += bytes_read;

                    /* Write to stdout */
                    size_t bytes_written = fwrite(read_buffer, 1U, bytes_read, stdout);

                    if (bytes_written != bytes_read)
                    {
                        fprintf(stderr, "\nError: Failed to write buffer to stdout\n");
                        operation_success = false;
                        break;
                    }
                }
                else
                {
                    /* Check for read error */
                    if (ferror(file_handle))
                    {
                        fprintf(stderr, "\nError: File read error occurred: %s\n",
                                strerror(errno));
                        operation_success = false;
                    }
                    /* EOF reached naturally - this is expected */
                    break;
                }
            }

            printf("\n-----------------------------------\n");
            printf("Total bytes read: %zu\n", total_bytes_read);

            /* Close file and check for errors */
            if (fclose(file_handle) != 0)
            {
                fprintf(stderr, "Warning: Error closing file '%s': %s\n",
                        file_path, strerror(errno));
                operation_success = false;
            }
            else
            {
                printf("File closed successfully\n");
            }
        }
    }

    return operation_success;
}

static void display_usage(const char *program_name)
{
    if (program_name != NULL)
    {
        fprintf(stderr, "Usage: %s <file_path>\n", program_name);
        fprintf(stderr, "Example: %s /path/to/file.txt\n", program_name);
    }
    else
    {
        fprintf(stderr, "Usage: program <file_path>\n");
    }
}
