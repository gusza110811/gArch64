def main():
    import matplotlib.pyplot as plt
    file_name = '.data'

    # Read numbers from the file
    numbers = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # ignore empty lines
                numbers.append(float(line))  # convert to float

    # Generate x-axis values (indices)
    x_values = list(range(1, len(numbers)+1))

    # Plot the numbers
    plt.plot(x_values, numbers)  # line graph with markers
    plt.title('Graph of execution time')
    plt.xlabel('Index')
    plt.ylabel('Time (ns)')
    plt.yscale('log')  # set y-axis to logarithmic
    plt.grid(True, which="both", ls="--")  # grid for better readability
    plt.show()

if __name__ == "__main__":
    main()