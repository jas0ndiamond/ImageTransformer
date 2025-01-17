import sys
import os
import logging
import time

import numpy as np

from PIL import Image

import dispy
import dispy.httpd

    # create cluster



#timeout after job submission and status report
dispy.config.MsgTimeout = 1200

dispy.MsgTimeout = 1200


#dispy.config.MstTimeout = 1200

    # import dispy's httpd module, create http server for this cluster

# class Cluster:
#     def __init__(self):
#
#
#     def shutdown():
#

class Grayscaler(object):
    def __init__(self, sourceImage):

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)


        # for file in files:
        #     print("constructor got file %s" % file)



        self.sourceImage = sourceImage

        #self.outputImage = None

        #TODO: throw exception if file doesn't exist

        #input is pixel tuple (r,g,b)
        #output is pixel tuple (r,g,b)




    def grayscalePixel(self, pix):
        #(r,g,b)

        # rPix = 0.299 * pix[0]
        # gPix = 0.587 * pix[1]
        # bPix = 0.114 * pix[2]

        #randomize the pixel just for test kicks
        #rPix = pix[ random.randint(1, 2) ]

        #scalars from internet dogma
        #take the average value, and set it as pixel values for each of r,g,b
        avg = int(
            (
                (0.299 * pix[0]) +
                (0.587 * pix[1]) +
                (0.114 * pix[2])
            )
            /3
        )

        return ( avg, avg, avg )

    # def setOutputDir(self, dir):
    #     self.outputDir = dir

    def grayscaleImage(self):
        from PIL import Image
        #output = img = None

        try:
            #sourceImage = Image.open(file)
            width, height = self.sourceImage.size

            #our ouput image
            outputImage = Image.new('RGB', (width, height))


            #outputPixels = img.load()

            pixelsProcessed = 0
            for x in range(width):
                for y in range(height):
                    pixel = self.sourceImage.getpixel( (x, y) )
                    #(42, 55, 48)

                    #print ("Found pixel %d,%d,%d" % pixel)

                    #convert pixel to grayscale and load it into pixels

                    outputImage.putpixel( (x,y) , self.grayscalePixel(pixel) )

                    pixelsProcessed += 1



            print("Processed pixels: %d" % pixelsProcessed)

            #output.save(outputFileName, "JPEG")
        finally:
            pass

        return outputImage

    # def start(self):
    #     print("starting")
    #
    #     for file in self.files:
    #         print("file %s" % file)
    #         outputFile = ("%s/%s_output.jpg" % (self.outputDir, os.path.basename(file) ) )
    #
    #         self.grayscaleImage( Image.open(file) ).save(outputFile, "JPEG")

###############################


def main(args):

    if(len(args) < 2):
        print("Need at least 1 file")
        exit(1);

    jobs = []

    print("launching cluster")

    cluster = dispy.JobCluster(Grayscaler.grayscaleImage, nodes=['192.168.1.129'], secret="derpy", depends=[Grayscaler], loglevel=logging.DEBUG,  ip_addr='192.168.1.244')



    http_server = dispy.httpd.DispyHTTPServer(cluster)

    #sleep just in case a host is slow to respond
    time.sleep(25)


    #expand image files into a list of jobs

    print("Submitting jobs")

    for file in args[1:]:
        data = Image.open(file)
        newjob = cluster.submit( Grayscaler( data ) )
        jobs.append(newjob)

    print("Jobs submitted")

    for job in jobs:
        job()
        if job.status != dispy.DispyJob.Finished:
            print('job %s failed: %s' % (job.id, job.exception))
        else:
            print('job %s finished: %s' % (job.id, job.result))

            job.result.save( ("output/output%d.jpg" % job.id), "JPEG")

    print("Waiting on job completion")

    cluster.print_status()

    if(http_server):
        http_server.shutdown()

    if(cluster):
        cluster.close()

###############################
if __name__ == "__main__":
    main(sys.argv)
