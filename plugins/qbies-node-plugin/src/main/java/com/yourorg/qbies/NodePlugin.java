
package com.yourorg.qbies;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.Bukkit;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
import java.net.*;
import java.util.*;

public final class NodePlugin extends JavaPlugin {
    private int taskId = -1;
    private String nodeId;
    private int heartbeatSec;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        nodeId = getOrCreateNodeId();
        heartbeatSec = getConfig().getInt("HEARTBEAT_SECONDS", 180);
        getLogger().info("[QBIES-Node] nodeId="+nodeId);
        taskId = Bukkit.getScheduler().runTaskTimerAsynchronously(this, this::heartbeat, 20L, 20L*heartbeatSec).getTaskId();
    }

    @Override
    public void onDisable() {
        if (taskId != -1) Bukkit.getScheduler().cancelTask(taskId);
    }

    private String getOrCreateNodeId(){
        try{
            Path f = getDataFolder().toPath().resolve("node.id");
            if(!Files.exists(getDataFolder().toPath())) Files.createDirectories(getDataFolder().toPath());
            if(Files.exists(f)) return Files.readString(f);
            String nid = UUID.randomUUID().toString();
            Files.writeString(f, nid);
            return nid;
        }catch(Exception e){
            return "node-"+System.currentTimeMillis();
        }
    }

    private void heartbeat(){
        try{
            JsonObject hb = new JsonObject();
            hb.addProperty("node_id", nodeId);
            hb.add("shards", new JsonArray()); // skeleton: not reporting held shards
            hb.addProperty("free_mb", 512);
            String url = getConfig().getString("COORD_URL") + "/heartbeat";
            String resp = postJSON(url, hb.toString());
            getLogger().info("[QBIES-Node] heartbeat ok");
        }catch(Exception e){
            getLogger().warning("[QBIES-Node] heartbeat failed: "+e.getMessage());
        }
    }

    private static String postJSON(String url, String json) throws Exception{
        HttpURLConnection c = (HttpURLConnection)new URL(url).openConnection();
        c.setRequestMethod("POST");
        c.setRequestProperty("Content-Type","application/json");
        c.setDoOutput(true);
        try(OutputStream os = c.getOutputStream()){
            os.write(json.getBytes());
        }
        try(InputStream is = c.getInputStream()){
            return new String(is.readAllBytes());
        }
    }
}
