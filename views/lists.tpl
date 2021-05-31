%rebase('dcbase.tpl', name="Select lists to count")
{{!boilerplate}}
<center>
%if defined('kvetch') and kvetch:
    <p>{{!kvetch}}</p>
%end

<p>Show counts from just certain lists</p>
<blockquote>
  <form action="/lists" method="post">
  <p><select name=l multiple size=20>
    %for l in mlists:
       <option>{{l}}</option>
    %end
  </select></p>
<p>
 <input type=submit name=d value="Hours">
 <input type=submit name=d value="Days">
</p>
</blockquote>