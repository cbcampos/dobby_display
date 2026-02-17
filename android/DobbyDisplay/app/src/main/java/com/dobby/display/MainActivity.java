package com.dobby.display;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.WindowManager;

import java.io.InputStream;
import java.util.Scanner;
import org.json.JSONObject;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Keep screen on
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        
        webView = new WebView(this);
        setContentView(webView);
        
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setMediaPlaybackRequiresUserGesture(false);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        
        webView.setWebViewClient(new WebViewClient());
        
        // Load from config
        String serverUrl = getServerUrl();
        webView.loadUrl(serverUrl);
    }

    private String getServerUrl() {
        try {
            InputStream is = getAssets().open("config.json");
            Scanner scanner = new Scanner(is).useDelimiter("\\A");
            String json = scanner.hasNext() ? scanner.next() : "";
            JSONObject obj = new JSONObject(json);
            return obj.getString("server_url");
        } catch (Exception e) {
            return "http://100.76.87.63:5000";
        }
    }

    @Override
    public void onBackPressed() {
        String serverUrl = getServerUrl();
        webView.loadUrl(serverUrl);
    }
}
