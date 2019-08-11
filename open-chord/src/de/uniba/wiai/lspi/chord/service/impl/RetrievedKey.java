package de.uniba.wiai.lspi.chord.service.impl;

import java.io.Serializable;
import java.util.Set;

/**
 * Class to store the retrieved values from chord ring along with the hop count.
 *
 */
public class RetrievedKey {
	/**
	 * Values for the specified key.
	 */
	private Set<Serializable> values;
	/**
	 * HopCount for the key - {@link HopCount}
	 */
	private HopCount hopcount;

	/**
	 * Returns the values.
	 * 
	 * @return
	 */
	public Set<Serializable> getValues() {
		return values;
	}

	/**
	 * Set the values.
	 * 
	 * @param values
	 */
	public void setValues(Set<Serializable> values) {
		this.values = values;
	}

	/**
	 * Returns the hop count value.
	 * 
	 * @return
	 */
	public HopCount getHopcount() {
		return hopcount;
	}

	/**
	 * Sets the hop count value.
	 * 
	 * @param hopcount
	 */
	public void setHopcount(HopCount hopcount) {
		this.hopcount = hopcount;
	}

}
