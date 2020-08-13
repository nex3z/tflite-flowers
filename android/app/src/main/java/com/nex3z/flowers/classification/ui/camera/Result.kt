package com.nex3z.flowers.classification.ui.camera

import android.graphics.Bitmap
import com.nex3z.flowers.classification.classifier.Recognition

data class Result(
    val image: Bitmap,
    val recognition: Recognition
)
