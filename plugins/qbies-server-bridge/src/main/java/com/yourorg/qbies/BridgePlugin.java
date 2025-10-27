
package com.yourorg.qbies;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import java.net.*;
import java.io.*;
import java.util.Base64;
import com.google.gson.*;

public final class BridgePlugin extends JavaPlugin {

    private String base;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        base = getConfig().getString("COORD_URL");
        getLogger().info("[QBIES-Bridge] Ready. COORD="+base);
    }

    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if (!cmd.getName().equalsIgnoreCase("dao")) return false;
        try{
            if (args.length >= 1 && args[0].equalsIgnoreCase("read")) {
                String file = args[1];
                int shard = Integer.parseInt(args[2]);
                String resp = get(base + "/fetch?file="+URLEncoder.encode(file, "UTF-8")+"&shard_id="+shard);
                JsonObject o = JsonParser.parseString(resp).getAsJsonObject();
                String msg = new String(Base64.getDecoder().decode(o.get("data_b64").getAsString()));
                sender.sendMessage("§a[QBIES] Fragment: §f"+msg);
                return true;
            }
            if (args.length >= 1 && args[0].equalsIgnoreCase("reincarnate")) {
                String soul = (sender instanceof Player) ? ((Player)sender).getUniqueId().toString() : "console";
                JsonObject body = new JsonObject();
                body.addProperty("soul_id", soul);
                body.addProperty("karma", 10);
                String resp = postJSON(base + "/dao/reincarnate", body.toString());
                JsonObject o = JsonParser.parseString(resp).getAsJsonObject();
                sender.sendMessage("§d[Tái sinh] " + o.get("message").getAsString());
                return true;
            }
            if (args.length >= 1 && args[0].equalsIgnoreCase("law")) {
                JsonObject body = new JsonObject();
                body.addProperty("chaos", 65);
                String resp = postJSON(base + "/dao/law", body.toString());
                JsonObject o = JsonParser.parseString(resp).getAsJsonObject();
                sender.sendMessage("§b[Luật] " + o.get("message").getAsString());
                return true;
            }
            if (args.length >= 1 && args[0].equalsIgnoreCase("timeline")) {
                JsonObject body = new JsonObject();
                body.addProperty("flavor", "alpha");
                String resp = postJSON(base + "/dao/timeline/branch", body.toString());
                JsonObject o = JsonParser.parseString(resp).getAsJsonObject();
                sender.sendMessage("§e[Timeline] " + o.get("message").getAsString());
                return true;
            }
        }catch(Exception e){
            sender.sendMessage("§c[QBIES] error: "+e.getMessage());
        }
        sender.sendMessage("§7Usage: /dao read <file> <shardId> | /dao reincarnate | /dao law | /dao timeline");
        return true;
    }

    private static String get(String url) throws Exception{
        HttpURLConnection c = (HttpURLConnection)new URL(url).openConnection();
        c.setRequestMethod("GET");
        try(InputStream is = c.getInputStream()){
            return new String(is.readAllBytes());
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
