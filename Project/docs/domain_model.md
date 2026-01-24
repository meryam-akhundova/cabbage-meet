# Domain Model for CabbageMeet
----

## **Entities** <br/>

&nbsp; **User**  <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; UserId  <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Name  <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Contact Information  <br/>
&nbsp;**Schedule** <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Owner ID <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Availablity Slots <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Last Updated <br/>
&nbsp;**Group** <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Group ID <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Name <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Description <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Created By <br/>
&nbsp;**Meeting** <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Description <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Who's Available <br/>
&nbsp;**Meeting Time** <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Start Time <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; End Time <br/>

----

## **Relationships** <br/>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; User owns Schedule <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; User belongs to a Group <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Group has multiple Users <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Group organizes Meeting <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Meeting includes Users <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Schedule decides Meeting Time <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Meeting happens during Meeting Time <br/>

