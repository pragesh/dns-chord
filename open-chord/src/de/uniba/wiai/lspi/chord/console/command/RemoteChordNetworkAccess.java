/***************************************************************************
 *                                                                         *
 *                          ChordNetworkAccess.java                        *
 *                            -------------------                          *
 *   date                 : 09.09.2004                                     *
 *   copyright            : (C) 2004-2008 Distributed and                  *
 *				Mobile Systems Group                       *
 *                              Lehrstuhl fuer Praktische Informatik       *
 *                              Universitaet Bamberg                       *
 *                              http://www.uni-bamberg.de/pi/              *
 *   email                : sven.kaffille@uni-bamberg.de                   *
 *   			karsten.loesing@uni-bamberg.de                 *
 *                                                                         *
 *                                                                         *
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   A copy of the license can be found in the license.txt file supplied   *
 *   with this software or at: http://www.gnu.org/copyleft/gpl.html        *
 *                                                                         *
 ***************************************************************************/

package de.uniba.wiai.lspi.chord.console.command;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Enumeration;

import de.uniba.wiai.lspi.chord.data.URL;
import de.uniba.wiai.lspi.chord.service.Chord;
import de.uniba.wiai.lspi.chord.service.impl.ChordImpl;

/**
 * @author sven
 * @version 1.0.5
 */
public final class RemoteChordNetworkAccess {

	int protocolType = URL.SOCKET_PROTOCOL; 
	
	/**
	 * Invisible constructor.
	 */
	private RemoteChordNetworkAccess() {
		/*
		 * nothing to do here. 
		 */
	}

	/**
	 * this is a singleton.
	 */
	private static final RemoteChordNetworkAccess uniqueInstance = new RemoteChordNetworkAccess();

	/**
	 * Provides unique instance of <code>RemoteChordNetworkAccess</code>.
	 * 
	 * @return Singleton instance of <code>RemoteChordNetworkAccess</code>.
	 */
	public static RemoteChordNetworkAccess getUniqueInstance() {
		return uniqueInstance;
	}

	/**
	 * contains one instance of a remote chord node
	 */
	private Chord chordInstance = null;

	/**
	 * Join a remote chord network with help of the provided
	 * <code>bootstrapURL</code>. <code>port</code> must be a valid port
	 * number.
	 * 
	 * @param bootstrapURL
	 * @param port
	 * @throws Exception
	 */
	void join(URL bootstrapURL, int port) throws Exception {
		if (this.chordInstance != null) {
			throw new Exception("Already joined chord network!");
		}
		this.chordInstance = new ChordImpl();
		URL acceptIncomingConnections = null;
		try {
                        //determine how to obtain ip-address on linux system. see bug 1510537. sven
//			String host = java.net.InetAddress.getLocalHost().getHostAddress();
			String host = getHostAddress();
			if ((port <= 0) || (port >= 65536)) {
				acceptIncomingConnections = new URL(
						URL.KNOWN_PROTOCOLS.get(this.protocolType) + "://" + host
								+ "/");
			} else {
				acceptIncomingConnections = new URL(
						URL.KNOWN_PROTOCOLS.get(this.protocolType) + "://" + host
								+ ":" + port + "/");
			}
		} catch (Exception e) {
			throw new Exception("Could not create url for this host!", e);
		}
		try {
			if (bootstrapURL == null) {
				this.chordInstance.create(acceptIncomingConnections);
			} else {
				this.chordInstance
						.join(acceptIncomingConnections, bootstrapURL);
			}
		} catch (Exception e) {
			/*
			 * join/create failed. Set instance to null, so that we can try
			 * again.
			 */
			this.chordInstance.leave();
			this.chordInstance = null;
			throw e;
		}
	}

	/**
	 * Leaves the remote chord network.
	 * 
	 * @throws Exception
	 */
	void leave() throws Exception {
		if (this.chordInstance == null) {
			/*
			 * Nothing to do here.
			 */
			return;
		}
		Chord chord = this.chordInstance;
		this.chordInstance = null;
		chord.leave();
	}

	/**
	 * @return Returns the chordInstance.
	 */
	Chord getChordInstance() {
		return this.chordInstance;
	}
	
	/**
	 * Retrieve the IP address of the host. In the case the host OS is not Linux,
	 * InetAddress.getHostAddress() is simply returned. If the host OS is Linux,
	 * additional steps are performed to avoid returning the loopback address
	 * (e.g. 127.0.0.1).
	 * 
	 * Source:
	 * http://sourceforge.net/p/open-chord/bugs/2/
	 * 
	 * @return the IP address of the host
	 * @throws Exception
	 */
	private String getHostAddress() throws Exception {
		try {
			if (System.getProperty("os.name").equals("Linux")) {
				Enumeration<NetworkInterface> e = NetworkInterface.getNetworkInterfaces();
				while (e.hasMoreElements()) {
					NetworkInterface netface = (NetworkInterface)e.nextElement();
					if (!netface.getName().equals("lo")) { 
						Enumeration<InetAddress> e2 = netface.getInetAddresses();
//						while (e2.hasMoreElements()){
//							e2.nextElement();
//							InetAddress ip = (InetAddress) e2.nextElement();
//							return ip.toString().substring(1);
//						}
						e2.nextElement();
						while (e2.hasMoreElements()) {
							InetAddress ip = (InetAddress) e2.nextElement();
							return ip.toString().substring(1);
						}
					}
				}
				throw new Exception("Unknow Exception");
			}else
				return java.net.InetAddress.getLocalHost().getHostAddress();
		}
		catch(Exception e){
			throw new Exception("Could not create url for this host!", e);
		}
	}
	
}