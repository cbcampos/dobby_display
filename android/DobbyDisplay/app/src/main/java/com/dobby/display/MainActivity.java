package com.dobby.display;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.WindowManager;

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
        
        // Enable audio autoplay
        // webSettings.setAutoplay(true); // Removed: API not available
        
        webView.setWebViewClient(new WebViewClient());
        
        // Load the display
        webView.loadUrl("http://100.105.30.20:5000");
    }

    @Override
    public void onBackPressed() {
        // Prevent back button from closing the app
        webView.loadUrl("http://100.105.30.20:5000");
    }
}
