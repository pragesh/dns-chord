package myapp.driver;

import java.io.FileWriter;
import java.io.IOException;
import java.io.Serializable;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import de.uniba.wiai.lspi.chord.com.Entry;
import de.uniba.wiai.lspi.chord.data.ID;
import de.uniba.wiai.lspi.chord.data.URL;
import de.uniba.wiai.lspi.chord.service.Chord;
import de.uniba.wiai.lspi.chord.service.ServiceException;
import de.uniba.wiai.lspi.chord.service.impl.Entries;
import de.uniba.wiai.lspi.chord.service.impl.HashFunction;
import de.uniba.wiai.lspi.chord.service.impl.RetrievedKey;

/**
 * This is the helper class to run all the methods related to chord
 * implementation.
 * 
 */
public class DriverHelper {
	/**
	 * Set of running nodes.
	 */
	private Set<Chord> runningNodes = new HashSet<Chord>();
	/**
	 * Set of temporary failed nodes.
	 */
	private Set<Chord> failedChordNodes = new HashSet<Chord>();
	/**
	 * Set of all nodes in the chord ring.
	 */
	private Set<Chord> allNodes = new HashSet<Chord>();
	/**
	 * DNS Data list
	 */
	private List<DNS> dnsDataList = new ArrayList<DNS>();
	/**
	 * Correctness test data
	 */
	private List<DNS> correctnessTestDataList = new ArrayList<DNS>();
	/**
	 * Line separator based on system.
	 */
	private String separator = System.getProperty("line.separator");
	/**
	 * Bootstrap node or the first node which creates the chord ring.
	 */
	private Chord bootStrapNode;
	/**
	 * Bootstrap node URL String
	 */
	private String bootStrapNodeURL = "://localhost:8080/";
	/**
	 * URL
	 */
	private URL bootStrapCompleteURL;
	/**
	 * Port number initial value to start ring.
	 */
	private int port = 8181;
	/**
	 * URL to entries Map
	 */
	private Map<URL, FailedNode> urlToEntriesMap = new HashMap<URL, FailedNode>();
	/**
	 * Number of failures.
	 */
	private int numberofFailures = 0;
	/**
	 * Random number to select the chord node randomly for lookup.
	 */
	Random rand = new Random();

	/**
	 * Constructor
	 * 
	 * @param args
	 */
	public DriverHelper(String[] args) {

	}

	/**
	 * Method to create bootstrap node.
	 * 
	 * @param m
	 *            int number of bits
	 */
	public void createBootStrapNode(int m) {
		HashFunction.getHashFunction(m / 8);
		String protocol = URL.KNOWN_PROTOCOLS.get(URL.LOCAL_PROTOCOL);
		URL localURL = null;
		try {
			localURL = new URL(protocol + bootStrapNodeURL);
			bootStrapCompleteURL = localURL;
		} catch (MalformedURLException e) {
			throw new RuntimeException(e);
		}
		Chord chord = new de.uniba.wiai.lspi.chord.service.impl.ChordImpl();

		try {
			// Creating the chord ring with the local URL.
			chord.create(localURL);
			allNodes.add(chord);
			System.out.println(chord.getID());
			bootStrapNode = chord;
		} catch (ServiceException e) {
			throw new RuntimeException(" Could not create DHT !", e);
		}
	}

	/**
	 * Method to create and join n-1 left nodes to the chord ring.
	 * 
	 * @param N
	 */
	public void createNNodes(int N) {
		for (int i = 0; i < N; i++) {
			joinNode(port + i);
			try {
				Thread.sleep(100);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * Helper method used to join a node at specified port number.
	 * 
	 * @param portNumber
	 *            int
	 */
	public void joinNode(int portNumber) {
		Chord chord = new de.uniba.wiai.lspi.chord.service.impl.ChordImpl();
		String protocol = URL.KNOWN_PROTOCOLS.get(URL.LOCAL_PROTOCOL);
		URL localURL = null;
		try {
			localURL = new URL(protocol + "://localhost:" + portNumber + "/");
		} catch (MalformedURLException e) {
			throw new RuntimeException(e);
		}
		URL bootstrapURL = null;
		try {
			bootstrapURL = new URL(protocol + bootStrapNodeURL);
		} catch (MalformedURLException e) {
			throw new RuntimeException(e);
		}
		try {
			chord.join(localURL, bootstrapURL);
			System.out.println(chord.getID());
			runningNodes.add(chord);
			allNodes.add(chord);
		} catch (ServiceException e) {
			throw new RuntimeException("Could not join DHT!", e);
		}

	}

	/**
	 * Method to insert data by reading the csv file and inserting the data in
	 * chord ring.
	 */
	public void insertData() {
		dnsDataList = CSVReader.read("./DNA_TempData.csv");
		for (DNS data : dnsDataList) {
			StringKey myKey = new StringKey(data.getWebsiteName());
			data.setMyKey(myKey);
			try {
				bootStrapNode.insert(myKey, data.getIpAddress());
			} catch (ServiceException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * Method to run queries.
	 * 
	 * @param numberofQueries
	 * @param probFailure
	 * @param runNumber
	 */
	public void runQueries(int numberofQueries, double probFailure, int runNumber) {
		FileWriter fileWriter = null;
		try {
			// Writing the results like hopcount, lookup success ratio, average
			// latency in this file.
			fileWriter = new FileWriter("./results_java.txt", true);
			int totalHopCount = 0;
			double totalLatency = 0.0;
			int totalSuccessFulLookUp = 0;
			int totalTimeouts = numberofQueries;
			for (int i = 0; i < numberofQueries; i++) {
				// Failure and making nodes up based upon a probability.
				probabilityFailure(probFailure);
				DNS data = randomlySelectData();
				Chord chord = randomlySelectChordNode();
				if (chord == null) {
					continue;
				}
				long startTime = System.currentTimeMillis();
				System.out.println("Query: " + data.getIpAddress());
				RetrievedKey retrievedKey = chord.retrieveWithHopCount(data.getMyKey());
				Set<Serializable> values = retrievedKey.getValues();
				if (values != null) {
					for (Serializable k : values) {
						String value = k.toString();
						if (value.equals(data.getIpAddress())) {
							totalSuccessFulLookUp += 1;
							totalTimeouts -= 1;
							break;
						}
					}
				}
				long endTime = System.currentTimeMillis();
				totalHopCount += retrievedKey.getHopcount().getCount();
				totalLatency += (endTime - startTime) / 1000.0;
			}
			StringBuilder sb = new StringBuilder();
			sb.append(runNumber);
			sb.append(",");
			sb.append(totalHopCount / (float) numberofQueries);
			sb.append(",");
			sb.append(totalLatency / (float) numberofQueries);
			sb.append(",");
			sb.append(totalSuccessFulLookUp / (float) numberofQueries);
			sb.append(",");
			sb.append(totalTimeouts / (float) numberofQueries);
			fileWriter.write(sb.toString());
			fileWriter.write(separator);
		} catch (IOException e1) {
			e1.printStackTrace();
		} catch (ServiceException e) {
			e.printStackTrace();
		} finally {
			try {
				if (fileWriter != null) {
					fileWriter.flush();
					fileWriter.close();
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * Method to randomly select data that will be queried.
	 * 
	 * @return {@link DNS}
	 */
	public DNS randomlySelectData() {
		Random rand = new Random();
		return dnsDataList.get(rand.nextInt(dnsDataList.size()));
	}

	/**
	 * Method to randomly select a node on which lookup request will be sent.
	 * 
	 * @return {@link Chord}
	 */
	public Chord randomlySelectChordNode() {

		if (allNodes.size() >= 1) {
			int randomNumber = rand.nextInt(allNodes.size());
			int i = 0;
			for (Chord chord : allNodes) {
				if (i == randomNumber) {
					System.out.println("Selected node: " + chord.getURL());
					return chord;
				}
			}
		}
		// It can't return null though.
		return bootStrapNode;
	}

	/**
	 * Method to fail and make temporary failed node alive based on passed
	 * probability.
	 * 
	 * @param probFailure
	 *            double
	 */
	public void probabilityFailure(double probFailure) {
		// Starting a failed node node randomly.
		Iterator failedNodesIt = failedChordNodes.iterator();
		while (failedNodesIt.hasNext()) {
			Chord chord = (Chord) failedNodesIt.next();
			if (Math.random() > probFailure) {
				System.out.println("Started the node: " + chord.getID());
				chord.setTempFailure(false);
				failedNodesIt.remove();
				runningNodes.add(chord);
			}
		}
		// Failing a running node randomly.
		Iterator it = runningNodes.iterator();
		while (it.hasNext()) {
			Chord chord = (Chord) it.next();
			if (Math.random() < probFailure) {
				System.out.println("Failed the node: " + chord.getID());
				failedChordNodes.add(chord);
				chord.setTempFailure(true);
				it.remove();
			}

		}
	}

	/**
	 * Method to save all key value pairs in a local variable. This is used to
	 * calculate the storage count when the shutdown command is fired.
	 * 
	 * @param mp
	 *            Map
	 * @param entries
	 *            Set<Entry>
	 */
	public void saveEntries(Map mp, Set<Entry> entries) {
		Iterator it = mp.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry pair = (Map.Entry) it.next();
			// System.out.println(pair.getKey() + " = " + pair.getValue());
			Set<Entry> entries1 = (Set<Entry>) pair.getValue();
			if (entries1 != null) {
				for (Entry entry1 : entries1) {
					Entry entry = new Entry(new ID(entry1.getId().id), entry1.getValue());
					entries.add(entry);
				}
			}

		}
	}

	/**
	 * Method to shutdown bootstrap node.
	 * 
	 * @param runNumber
	 * @return StringBuilder which contains information about storage and query
	 *         load to be logged in file.
	 */
	public StringBuilder shutDownBootStrapNode(int runNumber) {
		Entries entries = bootStrapNode.getEntries();
		Map<ID, Set<Entry>> entriesMap = entries.getEntries();
		Set<Entry> entriesSaved = new HashSet<Entry>();
		saveEntries(entriesMap, entriesSaved);
		int storageLoad = entriesSaved.size();
		int queryLoad = bootStrapNode.getLoadCount();
		try {
			bootStrapNode.leave();
		} catch (ServiceException e) {
			e.printStackTrace();
		}
		StringBuilder sb = new StringBuilder();
		sb.append(runNumber);
		sb.append(",");
		sb.append(storageLoad);
		sb.append(",");
		sb.append(queryLoad);
		return sb;
	}

	/**
	 * Method to shut down all the nodes.
	 * 
	 * @param runNumber
	 *            int
	 */
	public void shutDownAllNodes(int runNumber) {
		FileWriter fileWriter = null;
		try {
			fileWriter = new FileWriter("./results_2_java.txt", true);
			// Running nodes apart from bootstrap node.
			Iterator it = runningNodes.iterator();
			while (it.hasNext()) {
				Chord chord = (Chord) it.next();
				Entries entries = chord.getEntries();
				Map<ID, Set<Entry>> entriesMap = entries.getEntries();
				Set<Entry> entriesSaved = new HashSet<Entry>();
				saveEntries(entriesMap, entriesSaved);
				int storageLoad = entriesSaved.size();
				int queryLoad = chord.getLoadCount();
				chord.leave();
				it.remove();
				StringBuilder sb = new StringBuilder();
				sb.append(runNumber);
				sb.append(",");
				sb.append(storageLoad);
				sb.append(",");
				sb.append(queryLoad);
				fileWriter.write(sb.toString());
				fileWriter.write(separator);
			}
			// failedNodes
			Iterator failedNodesIt = failedChordNodes.iterator();
			while (failedNodesIt.hasNext()) {
				Chord chord = (Chord) failedNodesIt.next();
				Entries entries = chord.getEntries();
				Map<ID, Set<Entry>> entriesMap = entries.getEntries();
				Set<Entry> entriesSaved = new HashSet<Entry>();
				saveEntries(entriesMap, entriesSaved);
				int storageLoad = entriesSaved.size();
				int queryLoad = chord.getLoadCount();
				chord.leave();
				failedNodesIt.remove();
				StringBuilder sb = new StringBuilder();
				sb.append(runNumber);
				sb.append(",");
				sb.append(storageLoad);
				sb.append(",");
				sb.append(queryLoad);
				fileWriter.write(sb.toString());
				fileWriter.write(separator);
			}
			// bootStrapNode
			StringBuilder bootStrapSb = shutDownBootStrapNode(runNumber);
			fileWriter.write(bootStrapSb.toString());
			fileWriter.write(separator);

		} catch (IOException e1) {
			e1.printStackTrace();
		} catch (ServiceException e) {
			e.printStackTrace();
		} finally {
			try {
				if (fileWriter != null) {
					fileWriter.flush();
					fileWriter.close();
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

	}

	/**
	 * Method to test the correctness of the chord ring. It checks for the
	 * scenarios when a key-value pair exists in the ring then value returned
	 * should be correct. If the key is not present, the ring should not return
	 * any value.
	 */
	public void testCorrectness() {
		correctnessTestDataList = CSVReader.read("./CorrectnessData.csv");
		List<DNS> correctnessViolated = new ArrayList<DNS>();
		for (DNS data : correctnessTestDataList) {
			System.out.println("Data: " + data.getIpAddress() + "Value: " + data.getWebsiteName());
			StringKey myKey = new StringKey(data.getWebsiteName());
			data.setMyKey(myKey);
			try {
				Set<Serializable> values = bootStrapNode.retrieve(myKey);
				if (values != null && values.size() >= 1) {
					for (Serializable k : values) {
						String value = k.toString();
						if (value.equals(data.getIpAddress())) {
							System.out.println("Correctness Verified for: " + data.getWebsiteName());
							break;
						}
					}
				} else if (data.getIpAddress().equals("-1") && values != null && values.size() == 0) {
					System.out.println("Correctness Verified for: " + data.getWebsiteName());
				} else {
					correctnessViolated.add(data);
				}

			} catch (ServiceException e) {
				e.printStackTrace();
			}
		}
		// If there are any correctness violation it will write that to the
		// file.
		if (correctnessViolated.size() > 0) {
			FileWriter fileWriter = null;
			try {
				fileWriter = new FileWriter("./correctnessVerificationJava.txt", true);
				StringBuilder sb = new StringBuilder();
				sb.append("Correctness Violated");
				fileWriter.write(sb.toString());
				fileWriter.write(separator);
			} catch (IOException e) {
				e.printStackTrace();
			} finally {
				try {
					if (fileWriter != null) {
						fileWriter.flush();
						fileWriter.close();
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}

}
