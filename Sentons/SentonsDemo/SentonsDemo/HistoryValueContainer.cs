using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsDemo
{
    class HistoryValueContainer
    {
        public double value = 0;
        private Queue<double> values = new Queue<double>();
        private Queue<DateTime> timestamps = new Queue<DateTime>();
        private double ms, lowWeight;
        public HistoryValueContainer(double ms, double lowWeight)
        {
            this.ms = ms;
            this.lowWeight = lowWeight;
        }
        public void Update(double newValue, DateTime time)
        {
            values.Enqueue(newValue);
            timestamps.Enqueue(time);
            while (((TimeSpan)(time - timestamps.Peek())).TotalMilliseconds > ms)
            {
                values.Dequeue();
                timestamps.Dequeue();
            }
            double k = 2 * (1.0 / values.Count - lowWeight) / (values.Count - 1);
            double now = lowWeight;
            value = 0;
            foreach (double x in values)
            {
                value += x * now;
                now += k;
            }
        }
    }
}
