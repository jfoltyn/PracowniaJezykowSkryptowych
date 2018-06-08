#!/bin/bash

THIS_SCRIPT=$0

function calc {
    awk "BEGIN{print (${1})}"
}

function echo_bold {
    echo -e "\033[1m${1}\033[0m"
}

function echo_red {
    echo -e "\033[91m${1}\033[0m"
}

function show_help {
    echo_bold "Description"
    echo "  Script is orchestrating process of measuring algorithms speed. Each loop a maze is generated"
    echo "  and then both algorithms are solving it for chosen amount of times"
    echo
    echo_bold "Usage:"
    echo "  ${THIS_SCRIPT} [OPTIONS]"
    echo
    echo_bold "Options:"
    echo_bold "  -h"
    echo "    Shows this message"
    echo
    echo_bold "  -s size_of_generated_mazes"
    echo "    Size of maze must be must me natural number"
    echo "    Default: 10"
    echo
    echo_bold "  -m how_many_different_mazes"
    echo "    How many times new maze will be generated"
    echo "    Default: 2"
    echo
    echo_bold "  -i how_many_time_each_maze_to_solve"
    echo "    Describes how many times for each generated maze, algorithms will attempt to find a way through it"
    echo "    Default: 5"
    echo
    echo

    exit ${1}
}

function show_incorrect_args {
    echo_bold "$(echo_red "Incorrect options")"
    echo_red "Showing help:"
    echo
    show_help 1
}

ITERATIONS=2
SOLUTIONS_PER_MAZE=5
MAZE_SIZE=10

while getopts ":hm:i:s:" opt; do
    case ${opt} in
        h)
            show_help 0
            ;;
        m)
            if ! [[ ${OPTARG} =~ ^-?[0-9]+$ ]]; then
                show_incorrect_args
            elif (( $(calc "${OPTARG} < 1") )); then
                show_incorrect_args
            fi
            ITERATIONS=${OPTARG}
            ;;
        i)
            if ! [[ ${OPTARG} =~ ^-?[0-9]+$ ]]; then
                show_incorrect_args
            elif (( $(calc "${OPTARG} < 1") )); then
                show_incorrect_args
            fi
            SOLUTIONS_PER_MAZE=${OPTARG}
            ;;
        s)
            if ! [[ ${OPTARG} =~ ^-?[0-9]+$ ]]; then
                show_incorrect_args
            elif (( $(calc "${OPTARG} < 1") )); then
                show_incorrect_args
            fi
            MAZE_SIZE=${OPTARG}
            ;;
        \?)
            show_incorrect_args
            ;;
        :)
            show_incorrect_args
            ;;
    esac
done
shift $(($OPTIND - 1))

if ! [ -z ${1} ]; then
    show_incorrect_args
fi

MAZE_FILE_PATH='a.maze'

TOTAL_ASTAR_MAZE_SOLVING_DURATION=0
TOTAL_DIJKSTRA_MAZE_SOLVING_DURATION=0
for i in $(seq 1 ${ITERATIONS}); do
    ./MazeGenerator.pl ${MAZE_SIZE} > ${MAZE_FILE_PATH}

    MAZE_SOLVING_DURATION=$(./MazeSolver.py ${MAZE_FILE_PATH} -i ${SOLUTIONS_PER_MAZE} -a astar)
    TOTAL_ASTAR_MAZE_SOLVING_DURATION=$(calc "${TOTAL_ASTAR_MAZE_SOLVING_DURATION}+${MAZE_SOLVING_DURATION}")

    MAZE_SOLVING_DURATION=$(./MazeSolver.py ${MAZE_FILE_PATH} -i ${SOLUTIONS_PER_MAZE} -a dijkstra)
    TOTAL_DIJKSTRA_MAZE_SOLVING_DURATION=$(calc "${TOTAL_ASTAR_MAZE_SOLVING_DURATION}+${MAZE_SOLVING_DURATION}")
done


ASTAR_AVERAGE=$(calc "${TOTAL_ASTAR_MAZE_SOLVING_DURATION} / ${ITERATIONS}")
DIJKSTRA_AVERAGE=$(calc "${TOTAL_DIJKSTRA_MAZE_SOLVING_DURATION} / ${ITERATIONS}")
echo "Average time to solve maze using:"
echo "  A* -       ${ASTAR_AVERAGE}s"
echo "  Dijkstry - ${DIJKSTRA_AVERAGE}s"
echo

IS_ASTAR_FASTER=$(calc "${ASTAR_AVERAGE} < ${DIJKSTRA_AVERAGE}")
if (( ${IS_ASTAR_FASTER} )); then
    DIFFERENCE=$(calc "(${TOTAL_DIJKSTRA_MAZE_SOLVING_DURATION}-${TOTAL_ASTAR_MAZE_SOLVING_DURATION}) / ${TOTAL_DIJKSTRA_MAZE_SOLVING_DURATION}")
    PERCENTAGE_DIFFERENCE=$(calc "${DIFFERENCE} * 100")
    echo "A* was ${PERCENTAGE_DIFFERENCE}% faster on avererage"
else
    DIFFERENCE=$(calc "(${TOTAL_ASTAR_MAZE_SOLVING_DURATION}-${TOTAL_DIJKSTRA_MAZE_SOLVING_DURATION}) / ${TOTAL_ASTAR_MAZE_SOLVING_DURATION}")
    PERCENTAGE_DIFFERENCE=$(calc "${DIFFERENCE} * 100")
    echo "Dijkstra was ${PERCENTAGE_DIFFERENCE}% faster on average"
fi

rm ${MAZE_FILE_PATH}

exit 0