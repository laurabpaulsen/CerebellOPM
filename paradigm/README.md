# WP1_paradigm
This repository holds the code to run the experiment.

The experiment starts and ends with collection of resting state data. During the actual experiment, trains of electric stimulations are presented (with varying length) are presented followed by an omission. These sequences are grouped in blocks which have a constant interstimulus interval. Additionally, blocks of none stimulations serve as a baseline. 



### Notes for interacting with the stimulus current generator
Can be done in two ways:
1. Sending the triggers through the SCG -> one intensity that can be adjusted on the SCG
2. Sending byte-commands through a serial port (if we need to adjust the intensity from the code. May be relevant if different intensities are needed for upper and lower extremities)


? Question can we even have two different output electrodes?
