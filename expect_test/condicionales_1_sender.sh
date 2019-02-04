#!/bin/bash

let number=$RANDOM

if [ $number -gt 25000 ]; then
    echo "Where are you from??"
else
    echo "What's your age??"
fi

read response

echo "Your response was $response" 
