package qbieslink;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;

import java.net.HttpURLConnection;
import java.net.URL;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

/**
 * QCoreBridge - ĐỊA ĐẠO
 * Cầu nối Falix (Minecraft 1.21.8) -> Celestial QBIES Render (Thiên Đạo)
 * Gửi sự kiện "tick" định kỳ cho từng người chơi online.
 */
public class QCoreBridge extends JavaPlugin {

    // URL API Thiên Đạo (Render) – sửa nếu bạn dùng domain khác
    private static final String API_URL =
            "https://celestial-qbies-engine.onrender.com/process_event";

    // Khoảng thời gian gửi tick (tính bằng giây)
    private static final int TICK_INTERVAL_SECONDS = 60; // 60 giây một lần

    private Logger log;

    @Override
    public void onEnable() {
        this.log = getLogger();
        log.info("🌍 QCoreBridge (Địa Đạo) đã khởi động!");
        startAutoTickLoop();
    }

    @Override
    public void onDisable() {
        if (log != null) {
            log.info("🌍 QCoreBridge đã tắt.");
        }
    }

    /**
     * Vòng lặp tự động gửi sự kiện "tick" cho tất cả người chơi online.
     * Mỗi tick sẽ tăng một lượng linh khí ngẫu nhiên (1.0 - 3.0) và gửi lên Thiên Đạo.
     */
    private void startAutoTickLoop() {
        new BukkitRunnable() {
            @Override
            public void run() {
                if (Bukkit.getOnlinePlayers().isEmpty()) {
                    return;
                }

                for (Player player : Bukkit.getOnlinePlayers()) {
                    try {
                        double energyGain = 1.0 + Math.random() * 2.0; // 1.0 -> 3.0
                        String json = String.format(
                                "{\"type\":\"tick\",\"player\":\"%s\",\"energy\":%.2f}",
                                player.getName(), energyGain
                        );
                        int code = postJson(API_URL, json);
                        log.info("⚡ Sent tick for " + player.getName()
                                + " energy=" + String.format("%.2f", energyGain)
                                + " -> HTTP " + code);
                    } catch (Exception e) {
                        log.warning("⚠️ Lỗi gửi dữ liệu tu luyện cho "
                                + player.getName() + ": " + e.getMessage());
                    }
                }
            }
        }.runTaskTimerAsynchronously(
                this,
                20L,                                      // delay lần đầu 1 giây
                20L * TICK_INTERVAL_SECONDS               // lặp lại mỗi N giây
        );
    }

    /**
     * Gửi JSON tới API Thiên Đạo bằng HttpURLConnection (có sẵn trong JDK).
     */
    private int postJson(String api, String json) throws Exception {
        URL url = new URL(api);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(json.getBytes(StandardCharsets.UTF_8));
        }

        int code = conn.getResponseCode();

        // Đọc/đóng stream để kết nối sạch (không cần nội dung response)
        try {
            if (code >= 200 && code < 300) {
                conn.getInputStream().close();
            } else if (conn.getErrorStream() != null) {
                conn.getErrorStream().close();
            }
        } catch (Exception ignored) {}

        conn.disconnect();
        return code;
    }
}
