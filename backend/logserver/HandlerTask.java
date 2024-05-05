import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.TimeUnit;

public class HandlerTask implements Runnable {
    private final int port;

    public HandlerTask(int port) {
        this.port = port;
    }

    private boolean wait(InputStream inputStream, int minimumBytesAvailable, int timeout) throws IOException, InterruptedException {
        long timePast = 0;
        while (inputStream.available() < minimumBytesAvailable && timePast < timeout) {
            TimeUnit.MILLISECONDS.sleep(50);
            timePast += 100;
        }

        return inputStream.available() >= minimumBytesAvailable;
    }

    private void tryToCreateDir(String dirName) throws IOException {
        Path path = Paths.get(dirName);

        if (!Files.exists(path)) {
            Files.createDirectories(path);
        }
    }

    private void writeToFile(byte[] data) throws IOException {
        LocalDateTime date = LocalDateTime.now();
        String formattedDate = date.format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        String formattedTimePrecise = date.format(DateTimeFormatter.ofPattern("HH-mm-ss-SSS"));

        tryToCreateDir("logs/" + formattedDate);

        FileOutputStream fos = new FileOutputStream("logs/" + formattedDate + "/" + formattedTimePrecise + ".txt");
        fos.write(data);
        fos.close();
    }

    public void run() {
        try {
            tryToCreateDir("logs/");
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        ServerSocket serverSocket = null;
        while (true) {
            try {
                TimeUnit.MILLISECONDS.sleep(500);

                System.out.println("Managing port: " + port);
                serverSocket = new ServerSocket(port);

                while (true) {
                    System.out.println("-----------------------------------");
                    Socket socket = serverSocket.accept();
                    System.out.println("Connected: " + socket.getLocalSocketAddress());
                    if (!wait(socket.getInputStream(), 4, 200)) {
                        socket.close();
                        System.out.println("    Connection closed");
                        continue;
                    }

                    int length = ByteBuffer.wrap(socket.getInputStream().readNBytes(4)).getInt();
                    System.out.println("Packet length: " + length);
                    if (length > 0 && length < 1_000_000) {
                        if (!wait(socket.getInputStream(), length, 500)) {
                            socket.close();
                            System.out.println("    Connection closed");
                            continue;
                        }

                        byte[] data = socket.getInputStream().readNBytes(length);

                        writeToFile(data);
                    }

                    socket.close();
                    System.out.println("    Connection closed");
                }
            } catch (IOException | InterruptedException e) {
                e.printStackTrace(System.err);
                if (serverSocket != null) {
                    try {
                        serverSocket.close();
                    } catch (IOException ex) {
                        throw new RuntimeException(ex);
                    }
                }
                System.out.println("Restarting port: " + port);
            }
        }
    }
}
