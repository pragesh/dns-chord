package de.uniba.wiai.lspi.chord.service.impl;

/**
 * Java bean class to store hop counts.
 *
 */
public class HopCount {
	/**
	 * Number of hop counts.
	 */
	int count;

	/**
	 * Constructor
	 */
	public HopCount() {
		count = 0;
	}

	/**
	 * Increment the hop count.
	 */
	public void increment() {
		count++;
	}

	/**
	 * Returns the hop count value.
	 * 
	 * @return
	 */
	public int getCount() {
		return count;
	}

}
