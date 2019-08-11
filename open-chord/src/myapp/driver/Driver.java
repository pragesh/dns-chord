package myapp.driver;
/**
 * This is the driver program which will be called by monitor
 * program by passing different parameters.
 * 
 *
 */
public class Driver {
	/**
	 * Driver main program.
	 * @param args
	 */
	public static void main(String[] args) {
		DriverHelper helper = new DriverHelper(args);
		de.uniba.wiai.lspi.chord.service.PropertiesLoader.loadPropertyFile();
		int m = Integer.parseInt(args[0]);
		//In this implementation, m bits are converted into bytes array
		// and passing an arbitrary number of bits results in this implementation to fail.
		if(m <= 8)	{
			m = 16;
		} else {
			m = 32;
		}
		int nodes = Integer.parseInt(args[1]);
		int successor_list_size = Integer.parseInt(args[2]);
		int queries = Integer.parseInt(args[3]);
		double stabalization_delay_float = Double.parseDouble(args[4]);
		double fix_finger_delay_float = Double.parseDouble(args[5]);
		double check_pre_delay_float = Double.parseDouble(args[6]);
		double prob_failure = Double.parseDouble(args[7]);
		int run_number = Integer.parseInt(args[8]);
		// Setup System parameters here.
		System.setProperty("de.uniba.wiai.lspi.chord.service.impl.ChordImpl.StabilizeTask.interval",
				"" + (int)(stabalization_delay_float*10));
		System.setProperty("de.uniba.wiai.lspi.chord.service.impl.ChordImpl.FixFingerTask.interval",
				"" + (int)(fix_finger_delay_float*10));
		System.setProperty("de.uniba.wiai.lspi.chord.service.impl.ChordImpl.CheckPredecessorTask.interval",
				"" + (int)(check_pre_delay_float*10));
		System.setProperty("de.uniba.wiai.lspi.chord.service.impl.ChordImpl.successors", "" + successor_list_size);
		// Create BootStrap Node
		helper.createBootStrapNode(m);
		// Create N nodes
		helper.createNNodes(nodes - 1);
		// Insert Data
		helper.insertData();
		//Correctness Testing
		helper.testCorrectness();
		// LookUp Keys
		helper.runQueries(queries, prob_failure, run_number);
		// ShutDown Nodes
		helper.shutDownAllNodes(run_number);
		System.out.println("Process Exited");
	}
}