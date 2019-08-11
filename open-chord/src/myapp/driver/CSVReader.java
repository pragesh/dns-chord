package myapp.driver;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class to read the csv file.
 *
 */
public class CSVReader {
	/**
	 * Utility method to read the csv file for DNS data.
	 * 
	 * @param filePath
	 * @return List<DNS>
	 */
	public static List<DNS> read(String filePath) {
		List<DNS> dnsDataList = new ArrayList<DNS>();
		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = ",";
		try {
			br = new BufferedReader(new FileReader(filePath));
			// For Header
			br.readLine();
			while ((line = br.readLine()) != null) {
				String[] fileData = line.split(cvsSplitBy);
				DNS data = new DNS();
				data.setWebsiteName(fileData[0]);
				data.setIpAddress(fileData[1]);
				dnsDataList.add(data);
			}
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
		return dnsDataList;
	}

}