using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsReader
{
    public class SentonsReader
    {
        TouchReader.Reader reader;

        public SentonsReader()
        {
            reader = new TouchReader.Reader();
        }

        public void print(string s)
        {
            System.Console.Write(s+'\n');
        }

        public bool connect()
        {
            if (reader.connect())
            {
                print("Connect: Success");
                return true;
            }
            print("Connect: ERROR");
            print(reader.Status);
            return false;
        }

        public bool disconnect()
        {
            if (reader.disconnect())
            {
                print("Disconnect: Success");
                return true;
            }
            print("Disconnect: ERROR");
            print(reader.Status);
            return false;
        }

        public bool read()
        {
            if (!reader.Connected)
            {
                print("Read: Connecting first.");
                if (!connect())
                {
                    print("Read: Failed, could not connect.");
                    return false;
                }
            }
            if (!getNewTouches())
            {
                print("Read: Failed, could not read tracks");
                return false;
            }
            return true;
        }


        private bool getNewTouches()
        {
            TouchReader.TouchSet newestTouchSet;

            // Read the touches from the firmware
            if (!reader.Read())
            {
                print(String.Format("Read: Error reported [ {0} ]", reader.Status));
                return false;
            }

            // Retrieve the newest touches from the reader
            newestTouchSet = reader.LatestTouchSet;
            // Display my new touches (if any)
            printTouchSet(newestTouchSet);

            return true;
        }

        private void printTouchSet(TouchReader.TouchSet tset)
        {
            if (tset.touchList.Count == 0)
            {
                print("Read: no current touches.");
            }
            else
            {
                print("Bar ID, Track ID, Force, Pos0 mm, Pos1 mm, Pos2 mm");
                foreach (TouchReader.TouchReport touchReportEntry in tset.touchList)
                {
                    print(string.Format("{0,6}, {1,8}, {2,5:F0}, {3,7:F2}, {4,7:F2}, {5,7:F2}",
                                touchReportEntry.BarID, touchReportEntry.TrackID, touchReportEntry.force_lvl,
                                processSignedDiv16(touchReportEntry.pos0),
                                processSignedDiv16(touchReportEntry.pos1),
                                processSignedDiv16(touchReportEntry.pos2)));
                }
            }
        }

        public float processSignedDiv16(UInt16 data)
        {
            if (data <= 0x7FFF)
            {
                // We are positive
                return (Convert.ToSingle(data) / 16.0F);
            }
            // We are negative
            return ((Convert.ToSingle(data) - 0x10000) / 16.0F);
        }

    }
}
