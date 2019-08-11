package myapp.driver;

import java.util.Set;

import de.uniba.wiai.lspi.chord.com.Entry;
import de.uniba.wiai.lspi.chord.data.URL;

public class FailedNode {

	private Set<Entry> entries;
	private URL url;
	private int queryLoad;

	public Set<Entry> getEntries() {
		return entries;
	}

	public void setEntries(Set<Entry> entries) {
		this.entries = entries;
	}

	public URL getUrl() {
		return url;
	}

	public void setUrl(URL url) {
		this.url = url;
	}

	public int getQueryLoad() {
		return queryLoad;
	}

	public void setQueryLoad(int queryLoad) {
		this.queryLoad = queryLoad;
	}

}
