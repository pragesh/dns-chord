package myapp.driver;

import de.uniba.wiai.lspi.chord.service.Key;

/**
 * Class which implements {@link Key} interface to store website URL and ip
 * address in string key-value format.
 * 
 *
 */
public class StringKey implements Key {
	/**
	 * String representation of Key
	 */
	private String theString;

	/**
	 * Constructor
	 * 
	 * @param theString
	 */
	public StringKey(String theString) {
		this.theString = theString;
	}

	@Override
	public byte[] getBytes() {
		// TODO Auto-generated method stub
		return this.theString.getBytes();
	}

	public int hashCode() {
		return this.theString.hashCode();
	}

	public boolean equals(Object o) {
		if (o instanceof StringKey) {
			return ((StringKey) o).theString.equals(this.theString);
		}
		return false;
	}

	@Override
	public String toString() {
		return theString;
	}

}