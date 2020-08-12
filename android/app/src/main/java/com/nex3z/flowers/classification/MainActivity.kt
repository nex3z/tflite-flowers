package com.nex3z.flowers.classification

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.findNavController
import androidx.navigation.fragment.NavHostFragment
import kotlinx.android.synthetic.main.activity_main.*

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(findViewById(R.id.toolbar))
        init()
    }

    private fun init() {
        with ((supportFragmentManager.findFragmentById(R.id.fcv_cm_nav_host)
                as NavHostFragment).navController) {
            addOnDestinationChangedListener { _, destination, _ ->
                if(destination.id == R.id.camera_fragment) {
                    toolbar.visibility = View.GONE
                } else {
                    toolbar.visibility = View.VISIBLE
                }
            }
        }
    }
}