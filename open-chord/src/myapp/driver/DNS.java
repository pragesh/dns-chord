package myapp.driver;

/**
 * Bean class to store dns data.
 *
 */
public class DNS {
	/**
	 * Website name
	 */
	public String websiteName;
	/**
	 * IP Address
	 */
	public String ipAddress;
	/**
	 * StringKet
	 */
	public StringKey myKey;

	/**
	 * Returns the website name.
	 * 
	 * @return
	 */
	public String getWebsiteName() {
		return websiteName;
	}

	/**
	 * Sets the website name.
	 * 
	 * @param websiteName
	 */
	public void setWebsiteName(String websiteName) {
		this.websiteName = websiteName;
	}

	/**
	 * Returns the IP Address.
	 * 
	 * @return String IP Address
	 */
	public String getIpAddress() {
		return ipAddress;
	}

	/**
	 * Sets the IP Address.
	 * 
	 * @param ipAddress
	 *            String
	 */
	public void setIpAddress(String ipAddress) {
		this.ipAddress = ipAddress;
	}

	/**
	 * Returns string key
	 * 
	 * @return {@link StringKey}
	 */
	public StringKey getMyKey() {
		return myKey;
	}

	/**
	 * Sets the string key.
	 * 
	 * @param myKey
	 *            StringKey
	 */
	public void setMyKey(StringKey myKey) {
		this.myKey = myKey;
	}

}
