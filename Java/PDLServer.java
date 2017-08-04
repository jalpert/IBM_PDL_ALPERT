import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.URISyntaxException;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.concurrent.TimeoutException;

import org.openstack4j.api.storage.ObjectStorageService;
import org.openstack4j.model.common.Identifier;
import org.openstack4j.model.common.Payload;
import org.openstack4j.model.common.Payloads;
import org.openstack4j.openstack.OSFactory;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;

public class PDLServer
{
	public static void main(String...args)
	{
		new PDLServer();
	}
	
	//RabbitMQ Credentials
	String uri = "amqps://admin:GSEERXQSSFHPRWQG@portal-ssl120-4.bmix-dal-yp-caec71de-8add-471c-a7b5-f382e325cc49.jalpert911-gmail-com.composedb.com:17802/bmix-dal-yp-caec71de-8add-471c-a7b5-f382e325cc49";
	String incoming_queue = "PDL Incoming", outgoing_queue = "PDL Outgoing";
	private Connection conn;
	private Channel channel;

	// Openstack Object Storage Credentials
	String userId = "8f63ecdc574f48759560b779bdb161f6";
	String password = "BrNY!N]5Q4L3B_!s";
	String auth_url = "https://identity.open.softlayer.com" + "/v3";
	String domain = "1389989";
	String project = "object_storage_dec6d055_2c9a_46d4_a544_505079e4a4fd";
	
	File bin = new File("/home/pi/Desktop/PDL");
	File tmp = new File(bin, "tmp");
	
	public PDLServer()
	{	
		// Extract os + mq credentials
		JSONParser parser = new JSONParser();
		try
		{
			JSONObject osJSON = (JSONObject) parser.parse(new FileReader(new File(bin, "credentials.txt")));
			userId = (String) osJSON.get("userID");
			password = (String) osJSON.get("password");
			auth_url = (String) osJSON.get("auth_url");
			domain = (String) osJSON.get("domainName");
			project = (String) osJSON.get("project");
			
			//TODO: MQ
			
		}
		catch(ParseException ex)
		{
			ex.printStackTrace();
		}
	
		// Create the main directory and tmp directory
		bin.mkdir();
		tmp.mkdir();
		
		try {
			// Connect to Rabbit MQ service
			ConnectionFactory factory = new ConnectionFactory();
			factory.setUri(uri);
			conn = factory.newConnection();
			channel = conn.createChannel();

			channel.queueDeclare(incoming_queue, false, false, false, null);
			channel.queueDeclare(outgoing_queue, false, false, false, null);
		} catch (KeyManagementException | NoSuchAlgorithmException | URISyntaxException | IOException | TimeoutException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		Consumer consumer = new DefaultConsumer(channel)
		{
			@ Override
			public void handleDelivery(String consumerTag, Envelope envolope, AMQP.BasicProperties properties, byte [] body) throws IOException
			{
				// Process the message from the queue
				String msg = new String(body, "UTF-8");
				System.out.println(" [x] Received '" + msg + "'");
				
				// Parse  the message
				String [] strs = msg.split(";");
				String container = strs[0], filename = strs[1], framerate = strs[2], args = "";
				if(strs.length > 3)
					args = strs[3];
				
				try {
					// Connect to Openstack Object Storage
					ObjectStorageService os = OSFactory.builderV3()
							.endpoint(auth_url)
							.credentials(userId, password)
							.scopeToProject(Identifier.byName(project), Identifier.byName(domain))
							.authenticate().objectStorage();

					// Download the video file from object storage and store it in the directory bin/tmp
					File videoFile = new File(tmp, filename);
					os.objects().download(container,filename).writeToFile(videoFile);
					System.out.println(" [x] Successfully downloaded " + filename);
				
					// Run the python code
					ProcessBuilder pb = new ProcessBuilder();
					pb.directory(bin); // set the process's working directory
					
					// Keep a log
					//File log = new File(tmp, changeExtension(filename, "-log.txt"));
					//PrintWriter writer = new PrintWriter(log);
					pb.inheritIO();
					//pb.redirectInput(log);
					//pb.redirectOutput(log);
					//pb.redirectError(log);
					
					ArrayList<String> command = new ArrayList<String>();
					command.add("python");
					command.add(bin.getAbsolutePath() + "/Python/main.py");
					command.add(tmp.getAbsolutePath() + "/" + filename);
					command.add(framerate);
					if(!args.isEmpty())
					    for(String a: args.split(" "))
						command.add(a);
					pb.command(command);
					Process process = pb.start();
					int err = process.waitFor();
					System.out.println(" [x] Process completed. Any errors? " + (err == 0 ? "No" : "Yes"));
				
					// Upload the results back to object storage
					filename = changeExtension(filename, ".tsv");
					Payload<File> payload = Payloads.create(new File(tmp, filename));
					os.objects().put(container, filename, payload);
					
					filename = changeExtension(filename, ".png");
					payload = Payloads.create(new File(tmp, filename));
					os.objects().put(container, filename, payload);
					
					// Delete the video from the disk
					videoFile.delete();
				}
				catch(Exception ex)
				{
					ex.printStackTrace();
				}
				
				// Send an appropriate message back to the client
				msg = "All Done!";
				channel.basicPublish("", outgoing_queue, null, msg.getBytes());
				System.out.println(" [x] Sent " + msg + " back to client");
			}
		};
		
		try
		{
			channel.basicConsume(incoming_queue, true, consumer);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		System.out.println(" [x] Waiting for messages on " + incoming_queue + ". To exit press CTRL+C");
	}
	
	public static String changeExtension(String filename, String ext)
	{
		if(!ext.contains("."))
			ext = "." + ext;
		return filename.substring(0, filename.lastIndexOf('.')) + ext;
	}
}
