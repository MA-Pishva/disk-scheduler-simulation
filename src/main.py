from copy import copy
from random import uniform, randint
import matplotlib.pyplot as plt

HEAD_DELAY = 1
TRACK_TRAVERSED_IN_ONE_MS = 4000


def main():
    menu()


def reader():
    head = int(input())
    k = int(input())
    cylinder, time = list(), list()

    for i in range(k):
        c, t = converter(input().split())
        cylinder.insert(i, c)
        time.insert(i, t)

    return head, cylinder, time


def converter(entry):
    return int(entry[0]), int(entry[1])


def elevator(head_position, requested_cylinder, request_times, rotational_latency, transfer_time):
    responsed_cylinder, response_times = list(), list()
    # move up = 1, move down = 0, no move = -1
    elapsed_time, end_index, move = 0.0, 0, -1
    track_read_time = rotational_latency + transfer_time

    while requested_cylinder:
        end_index = requested_received(request_times, elapsed_time)

        if end_index == -1:
            elapsed_time = request_times[0]
            continue

        response_index, move = select_request(move, end_index, requested_cylinder, head_position)

        if response_index == -1:
            continue

        mid_way_cylinders = midway_requests(
            head_position, response_index, requested_cylinder, request_times, elapsed_time, move
        )

        (
            responsed_cylinder,
            response_times,
            elapsed_time,
            requested_cylinder,
            request_times,
            head_position,
            response_index,
            end_index,
        ) = response_midway_requested(
            head_position,
            requested_cylinder,
            request_times,
            responsed_cylinder,
            response_times,
            elapsed_time,
            mid_way_cylinders,
            response_index,
            rotational_latency,
            transfer_time,
            end_index,
        )

        head_time = cylinder_distance(requested_cylinder[response_index], head_position)
        if move != -1:
            elapsed_time += head_time + HEAD_DELAY + track_read_time
        else:
            elapsed_time += track_read_time

        response_times.append(elapsed_time)
        responsed_cylinder.append(requested_cylinder[response_index])
        head_position = requested_cylinder[response_index]

        del request_times[response_index]
        del requested_cylinder[response_index]

        if response_index <= end_index:
            end_index -= 1

    return responsed_cylinder, response_times


def fcfs(head_position, requested_cylinder, request_time, rotational_latency, transfer_time):
    responsed_cylinder, response_times, elapsed_time = list(), list(), 0.0
    track_read_time = rotational_latency + transfer_time

    for i in range(len(requested_cylinder)):
        if elapsed_time < request_time[i]:
            elapsed_time += request_time[i] - elapsed_time

        distance = cylinder_distance(requested_cylinder[i], head_position)

        if distance > 0:
            elapsed_time = elapsed_time + distance + HEAD_DELAY + track_read_time
        else:
            elapsed_time = elapsed_time + track_read_time

        response_times.insert(i, elapsed_time)
        responsed_cylinder.insert(i, requested_cylinder[i])
        head_position = requested_cylinder[i]

    return responsed_cylinder, response_times


def cylinder_distance(requested_cylinder, head_position):
    return abs((requested_cylinder - head_position) / TRACK_TRAVERSED_IN_ONE_MS)


def requested_received(request_time, elapsed_time):
    right = len(request_time) - 1
    result = -1
    left = 0

    while left <= right:
        mid = (left + right) // 2

        if mid == len(request_time) - 1:
            result = mid

        if request_time[mid] > elapsed_time:
            result = mid - 1
            right = mid - 1
        else:
            left = mid + 1

    return result


def midway_requests(head_position, request_index, requested_cylinder, request_times, elapsed_time, move):
    cylinders = list()

    for i in range(len(request_times)):
        elapsed_time_to_mid_request = abs(requested_cylinder[i] - head_position) // TRACK_TRAVERSED_IN_ONE_MS
        if move == 1:
            if (
                head_position < requested_cylinder[i] < requested_cylinder[request_index]
                and elapsed_time_to_mid_request + elapsed_time >= request_times[i]
            ):
                cylinders.insert(0, requested_cylinder[i])
        elif move == 0:
            if (
                head_position > requested_cylinder[i] > requested_cylinder[request_index]
                and elapsed_time_to_mid_request + elapsed_time >= request_times[i]
            ):
                cylinders.insert(0, requested_cylinder[i])

    if cylinders:
        if move == 1:
            cylinders.sort()
        else:
            cylinders.sort(reverse=True)

    return cylinders


def response_midway_requested(
    head_position,
    requested_cylinder,
    request_times,
    responsed_cylinder,
    response_times,
    elapsed_time,
    mid_way_cylinders,
    response_index,
    rotational_latency,
    transfer_time,
    end_index,
):
    track_read_time = rotational_latency + transfer_time
    for cylinder in mid_way_cylinders:
        head_time = cylinder_distance(cylinder, head_position)
        elapsed_time += head_time + HEAD_DELAY + track_read_time

        responsed_cylinder.append(cylinder)
        response_times.append(elapsed_time)
        head_position = cylinder

        index = requested_cylinder.index(cylinder)
        del request_times[index]
        del requested_cylinder[index]

        if index < response_index:
            response_index -= 1
        if index <= end_index:
            end_index -= 1

    return (
        responsed_cylinder,
        response_times,
        elapsed_time,
        requested_cylinder,
        request_times,
        head_position,
        response_index,
        end_index,
    )


def select_request(move, end_index, requested_cylinder, head_position):
    if move == -1:
        if requested_cylinder[0] > head_position:
            return 0, 1
        elif requested_cylinder[0] < head_position:
            return 0, 0
        else:
            return 0, -1

    elif move == 1:
        for i in range(end_index + 1):
            if requested_cylinder[i] >= head_position:
                return i, move
        return -1, 0
    else:
        for i in range(end_index + 1):
            if requested_cylinder[i] <= head_position:
                return i, move
        return -1, 1


def sort_requests(requested_cylinder, request_times, move=1):
    combined_lists = list(zip(requested_cylinder, request_times))
    if move == 1:
        sorted_combined_lists = sorted(combined_lists, key=lambda x: x[1])
    else:
        sorted_combined_lists = sorted(combined_lists, key=lambda x: x[1], reverse=True)
    requested_cylinder, request_times = zip(*sorted_combined_lists)

    return list(requested_cylinder), list(request_times)


def print_solution(
    elevator_cylinder_responsed, elevator_time_responsed, fcfs_cylinder_responsed, fcfs_time_responsed
):
    print(14 * " ", "Elevator", 41 * " ", "FCFS")
    print("Cylinder of request", 5 * " ", "Time request", 10 * " ", "Cylinder of request", 4 * " ", "Time request")

    for i in range(len(elevator_cylinder_responsed)):
        print(
            f"{str(elevator_cylinder_responsed[i]):<19s}",
            5 * " ",
            f"{str(round(elevator_time_responsed[i], 1)):<12s}",
            10 * " ",
            f"{str(fcfs_cylinder_responsed[i]):<19s}",
            5 * " ",
            f"{str(round(fcfs_time_responsed[i], 1)):<12s}",
        )


def manual_input():
    head_position, requested_cylinder, request_times = reader()
    requested_cylinder, request_times = sort_requests(requested_cylinder, request_times)
    rotational_latency, transfer_time = 4.17, 0.13

    elevator_cylinder_responsed, elevator_time_responsed = elevator(
        copy(head_position),
        copy(requested_cylinder),
        copy(request_times),
        rotational_latency,
        transfer_time,
    )
    fcfs_cylinder_responsed, fcfs_time_responsed = fcfs(
        head_position, requested_cylinder, request_times, rotational_latency, transfer_time
    )

    print_solution(
        elevator_cylinder_responsed, elevator_time_responsed, fcfs_cylinder_responsed, fcfs_time_responsed
    )


def random_generator():
    print("Please enter the number of random trials you want to generate: ")
    user_input = int(input())

    requested_cylinder = [[randint(0, 100000) for _ in range(100)] for _ in range(user_input)]
    requested_times = [[randint(0, 100) for _ in range(100)] for _ in range(user_input)]
    head_position = [randint(0, 100000) for _ in range(user_input)]
    rotational_latency = [round(uniform(2.0, 8.0), 2) for _ in range(user_input)]
    transfer_time = [round(uniform(0.01, 0.20), 2) for _ in range(user_input)]

    elevator_last_times, fcfs_last_times = list(), list()
    elevator_average, fcfs_average = [0.0 for _ in range(100)], [0.0 for _ in range(100)]

    for i in range(user_input):
        requested_cylinder_i, requested_times_i = sort_requests(requested_cylinder[i], requested_times[i])
        head_position_i, rotational_latency_i, transfer_time_i = (
            head_position[i],
            rotational_latency[i],
            transfer_time[i],
        )

        _, fcfs_time_responsed = fcfs(
            copy(head_position_i),
            copy(requested_cylinder_i),
            copy(requested_times_i),
            copy(rotational_latency_i),
            copy(transfer_time_i),
        )
        _, elevator_time_responsed = elevator(
            head_position_i, requested_cylinder_i, requested_times_i, rotational_latency_i, transfer_time_i
        )

        elevator_last_times.append(elevator_time_responsed[-1])
        fcfs_last_times.append(fcfs_time_responsed[-1])

        elevator_average = [x + y / user_input for x, y in zip(elevator_average, elevator_time_responsed)]
        fcfs_average = [x + y / user_input for x, y in zip(fcfs_average, fcfs_time_responsed)]

    x_values = range(1, min(len(elevator_average), len(fcfs_average)) + 1)

    plt.plot(x_values, elevator_average[: len(x_values)], label="Elevator Algorithm", color="b")
    plt.plot(x_values, fcfs_average[: len(x_values)], label="FCFS Algorithm", color="r")
    plt.xlabel("Request Index")
    plt.ylabel("Average Completion Time (ms)")
    plt.title("Average Completion Time per Request Rank")
    plt.legend()
    plt.show()

    x_values = range(1, user_input + 1)

    plt.plot(x_values, elevator_last_times, label="Elevator Algorithm", color="b")
    plt.plot(x_values, fcfs_last_times, label="FCFS Algorithm", color="r")
    plt.xlabel("Trial Number")
    plt.ylabel("Total Makespan (ms)")
    plt.title("Total Workload Makespan: Elevator vs. FCFS")
    plt.legend()
    plt.show()


def menu():
    while True:
        print("Please select an option:")
        print("1- Enter manual workload input")
        print("2- Run random Monte Carlo benchmark")
        print("3- Exit")

        user_input = int(input())
        if user_input == 1:
            manual_input()
        elif user_input == 2:
            random_generator()
        elif user_input == 3:
            break
        else:
            print("Error: Please select an option between 1 and 3!")


if __name__ == "__main__":
    main()
